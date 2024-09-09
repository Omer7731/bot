import logging
import os
import json
import time
import random
from os import path
from random import shuffle, sample, randint

from atomicwrites import atomic_write

from GramAddict.core.decorators import run_safely
from GramAddict.core.interaction import _browse_carousel, register_like
from GramAddict.core.plugin_loader import Plugin
from GramAddict.core.utils import open_instagram_with_url, validate_url
from GramAddict.core.views import MediaType, OpenedPostView, Owner, PostsViewList

logger = logging.getLogger(__name__)

class LikeFromURLs(Plugin):
    """Likes a post from URL. The URLs are read from a plaintext file"""

    def __init__(self):
        super().__init__()
        self.description = (
            "Likes a post from URL. The URLs are read from a plaintext file"
        )
        self.arguments = [
            {
                "arg": "--likes-from-file",
                "help": "full path of plaintext file that contains URLs to like with range",
                "nargs": "+",
                "default": None,
                "metavar": ("postlist1.txt", "1-20"),
                "operation": True,
            }
        ]
        self.interacted_urls = set()  # To track URLs already interacted with
        self.json_filename = None

    def run(self, device, configs, storage, sessions, profile_filter, plugin):
        class State:
            def __init__(self):
                pass

            is_job_completed = False

        self.args = configs.args
        self.device = device
        self.device_id = configs.args.device
        self.state = None
        self.sessions = sessions
        self.session_state = sessions[-1]
        self.current_mode = plugin

        # Load interacted URLs from JSON file
        self.json_filename = os.path.join(storage.account_path, "interacted_urls.json")
        self.load_interacted_urls()

        # Parse file list and ranges from config
        file_list = self.parse_likes_from_file(self.args.likes_from_file)
        logger.info(f"Processing the following text files: {file_list}")  # Debug the file list

        shuffle(file_list)  # Randomize the order of files

        for filename, url_range in file_list:
            self.state = State()

            @run_safely(
                device=self.device,
                device_id=self.device_id,
                sessions=self.sessions,
                session_state=self.session_state,
                screen_record=self.args.screen_record,
                configs=configs,
            )
            def job():
                self.process_file(filename, storage, url_range)

            job()

        # Save all interacted URLs to JSON after finishing
        self.save_interacted_urls()

    def load_interacted_urls(self):
        """Loads interacted URLs from the JSON file"""
        if os.path.isfile(self.json_filename):
            with open(self.json_filename, "r", encoding="utf-8") as f:
                try:
                    self.interacted_urls = set(json.load(f))
                except json.JSONDecodeError:
                    logger.warning(f"Failed to load interacted URLs from {self.json_filename}. Starting with an empty list.")
                    self.interacted_urls = set()
        else:
            logger.info(f"No interacted URLs file found. Starting fresh.")

    def save_interacted_urls(self):
        """Saves the interacted URLs to a JSON file"""
        with open(self.json_filename, "w", encoding="utf-8") as f:
            json.dump(list(self.interacted_urls), f, indent=4)
        logger.info(f"Interacted URLs saved to {self.json_filename}.")

    def sample_sources(self, sources, n_sources):
        """Samples a random number of URLs based on a range defined in the config file"""
        sources_limit_input = n_sources.split("-")
        if len(sources_limit_input) > 1:
            sources_limit = randint(
                int(sources_limit_input[0]), int(sources_limit_input[1])
            )
        else:
            sources_limit = int(sources_limit_input[0])
        
        if len(sources) < sources_limit:
            sources_limit = len(sources)
        
        if sources_limit == 0:
            truncated = sources
            shuffle(truncated)
        else:
            truncated = sample(sources, sources_limit)
            logger.info(
                f"Source list truncated at {len(truncated)} {'item' if len(truncated)<=1 else 'items'}."
            )
        
        logger.info(
            f"In this session, {'that source' if len(truncated)<=1 else 'these sources'} will be handled: {', '.join(truncated)}"
        )
        return truncated

    def parse_likes_from_file(self, likes_from_file_config):
        """
        Parses the likes-from-file configuration which includes both filenames and ranges.
        Expected format: ["post.txt 1-7,"]
        Returns a list of tuples: [(filename, range), ...]
        """
        file_list = []
        for item in likes_from_file_config:
            # Remove any commas or trailing spaces
            item = item.strip(",")
            parts = item.split()

            # Ensure there are both filename and range
            if len(parts) == 2:
                filename = parts[0]
                url_range = parts[1]
                file_list.append((filename, url_range))
            else:
                logger.warning(f"Invalid entry in likes-from-file: {item}")
        return file_list

    def process_file(self, current_file, storage, url_range):
        """
        Processes the given text file, extracts URLs, and ensures they are interacted with if
        they haven't been already (as tracked by the interacted_urls set). After interaction, 
        the URL will be deleted from the file and stored in the JSON.
        """
        opened_post_view = OpenedPostView(self.device)
        post_view_list = PostsViewList(self.device)
        
        # Log the filename for debugging
        logger.info(f"Account path: {storage.account_path}, Current file: {current_file}")
        filename: str = os.path.join(storage.account_path, current_file)
        logger.info(f"Full file path: {filename}")

        if path.isfile(filename):
            with open(filename, "r", encoding="utf-8") as f:
                nonempty_lines = [line.strip("\n") for line in f if line.strip()]  # Check non-empty lines
                logger.info(f"In this file, there are {len(nonempty_lines)} URLs.")  # Log the number of URLs

                # If no URLs found, log and return
                if len(nonempty_lines) == 0:
                    logger.warning(f"No URLs found in the file {filename}.")
                    return

                # Use sample_sources to randomly select a number of URLs from the file based on the range
                selected_urls = self.sample_sources(nonempty_lines, url_range)

            # Process each selected URL
            for url in selected_urls:
                url = url.strip()

                # Check if the URL has already been interacted with
                if url in self.interacted_urls:
                    logger.info(f"URL {url} already interacted with. Skipping.")
                    continue

                # Process the URL if valid and not interacted with before
                if validate_url(url) and open_instagram_with_url(url):
                    if "instagram.com/p/" in url:
                        self.process_photo_or_carousel(opened_post_view, post_view_list, url, storage)
                    elif "instagram.com/tv/" in url or "instagram.com/reel/" in url:
                        self.process_igtv_or_reel(opened_post_view, url)

                    # Add URL to interacted list after interaction
                    self.interacted_urls.add(url)

                    # Save interacted URLs to JSON after each URL interaction
                    self.save_interacted_urls()

                    # Remove the interacted URL from the file
                    with open(filename, "r", encoding="utf-8") as file:
                        lines = file.readlines()
                    with open(filename, "w", encoding="utf-8") as file:
                        for line in lines:
                            if line.strip("\n") != url:
                                file.write(line)
                        logger.info(f"URL {url} removed from {filename}.")

                # Ensure back navigation happens first
                logger.info("Going back to previous screen..")
                try:
                    self.device.back()
                    logger.info("Successfully navigated back.")
                except Exception as e:
                    logger.error(f"Error during back navigation: {str(e)}")

                # Now, sleep before moving on to the next URL
                try:
                    sleep_time = random.randint(10, 25)
                    logger.info(f"Starting sleep for {sleep_time} seconds before opening the next URL.")
                    time.sleep(sleep_time)
                    logger.info(f"Finished sleeping for {sleep_time} seconds.")
                except Exception as e:
                    logger.error(f"Error during sleep: {str(e)}")
        else:
            logger.warning(f"File {current_file} not found.")
            return



    def process_photo_or_carousel(self, opened_post_view, post_view_list, url, storage):
        """Processes photo, carousel, and video media types"""
        like_succeed = False  # Initialize like_succeed to a default value

        # Extract media container and detect media type
        media, content_desc = post_view_list._get_media_container()  
        media_type, obj_count = post_view_list.detect_media_type_new(content_desc)

        # Watch the media based on its type
        if media_type == MediaType.PHOTO:
            logger.info("Detected a photo.")
            opened_post_view.watch_media(media_type)

        elif media_type == MediaType.CAROUSEL:
            if obj_count > 1:
                logger.info(f"Detected a carousel with {obj_count} items.")
                _browse_carousel(self.device, obj_count)
            opened_post_view.watch_media(media_type)

        elif media_type == MediaType.VIDEO:
            logger.info("Detected a video.")
            opened_post_view.watch_media(media_type)

        # Introduce random sleep time (4-8 seconds) after watching the media
        sleep_time = random.uniform(3, 8)
        logger.info(f"Waiting for {sleep_time:.2f} seconds before checking if post is liked.")
        time.sleep(sleep_time)

        # Check if the post is already liked after watching the media
        already_liked, _ = opened_post_view._is_post_liked()

        if already_liked:
            logger.info("Post already liked!")
        else:
            like_succeed = opened_post_view.like_post()

        username, _, _ = post_view_list._post_owner(self.current_mode, Owner.GET_NAME)
        if like_succeed:
            register_like(self.device, self.session_state)
            logger.info(f"Like for: {url}, status: {like_succeed}")
            storage.add_interacted_user(username, self.session_state.id, liked=1)
        else:
            logger.info("Not able to like this post!")




    def process_igtv_or_reel(self, opened_post_view, url):
        """Processes IGTV and Reels media types"""
        media_type = MediaType.REEL if "reel" in url else MediaType.IGTV

        # Watch the media first
        opened_post_view.watch_media_from_url(media_type)

        already_liked, _ = opened_post_view._is_video_liked()
        if already_liked:
            logger.info("Video already liked!")
        else:
            opened_post_view.like_video_from_url()
            logger.debug("Video liked and closing...")
