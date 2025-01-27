import os
import logging
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from lyrics_transcriber.types import (
    LyricsData,
    TranscriptionResult,
    CorrectionResult,
)
from lyrics_transcriber.transcribers.base_transcriber import BaseTranscriber
from lyrics_transcriber.transcribers.audioshake import AudioShakeTranscriber, AudioShakeConfig
from lyrics_transcriber.transcribers.whisper import WhisperTranscriber, WhisperConfig
from lyrics_transcriber.lyrics.base_lyrics_provider import BaseLyricsProvider, LyricsProviderConfig
from lyrics_transcriber.lyrics.genius import GeniusProvider
from lyrics_transcriber.lyrics.spotify import SpotifyProvider
from lyrics_transcriber.output.generator import OutputGenerator
from lyrics_transcriber.correction.corrector import LyricsCorrector
from lyrics_transcriber.core.config import TranscriberConfig, LyricsConfig, OutputConfig


@dataclass
class LyricsControllerResult:
    """Holds the results of the transcription and correction process."""

    # Results from different sources
    lyrics_results: List[LyricsData] = field(default_factory=list)
    transcription_results: List[TranscriptionResult] = field(default_factory=list)

    # Corrected results
    transcription_corrected: Optional[CorrectionResult] = None

    # Output files
    lrc_filepath: Optional[str] = None
    ass_filepath: Optional[str] = None
    video_filepath: Optional[str] = None
    mp3_filepath: Optional[str] = None
    cdg_filepath: Optional[str] = None
    cdg_zip_filepath: Optional[str] = None
    original_txt: Optional[str] = None
    corrected_txt: Optional[str] = None
    corrections_json: Optional[str] = None


class LyricsTranscriber:
    """
    Controller class that orchestrates the lyrics transcription workflow:
    1. Fetch lyrics from internet sources
    2. Run multiple transcription methods
    3. Correct transcribed lyrics using fetched lyrics
    4. Generate output formats (LRC, ASS, video)
    """

    def __init__(
        self,
        audio_filepath: str,
        artist: Optional[str] = None,
        title: Optional[str] = None,
        transcriber_config: Optional[TranscriberConfig] = None,
        lyrics_config: Optional[LyricsConfig] = None,
        output_config: Optional[OutputConfig] = None,
        transcribers: Optional[Dict[str, BaseTranscriber]] = None,
        lyrics_providers: Optional[Dict[str, BaseLyricsProvider]] = None,
        corrector: Optional[LyricsCorrector] = None,
        output_generator: Optional[OutputGenerator] = None,
        logger: Optional[logging.Logger] = None,
        log_level: int = logging.DEBUG,
        log_formatter: Optional[logging.Formatter] = None,
    ):
        # Set up logging
        self.logger = logger or logging.getLogger(__name__)
        if not logger:
            self.logger.setLevel(log_level)
            if not self.logger.handlers:
                handler = logging.StreamHandler()
                formatter = log_formatter or logging.Formatter("%(asctime)s - %(levelname)s - %(module)s - %(message)s")
                handler.setFormatter(formatter)
                self.logger.addHandler(handler)

        self.logger.debug(f"LyricsTranscriber instantiating with input file: {audio_filepath}")

        # Store configs (with defaults if not provided)
        self.transcriber_config = transcriber_config or TranscriberConfig()
        self.lyrics_config = lyrics_config or LyricsConfig()
        self.output_config = output_config or OutputConfig()

        # Basic settings
        self.audio_filepath = audio_filepath
        self.artist = artist
        self.title = title
        self.output_prefix = f"{artist} - {title}" if artist and title else os.path.splitext(os.path.basename(audio_filepath))[0]

        # Add after creating necessary folders
        self.logger.debug(f"Using cache directory: {self.output_config.cache_dir}")
        self.logger.debug(f"Using output directory: {self.output_config.output_dir}")

        # Create necessary folders
        os.makedirs(self.output_config.cache_dir, exist_ok=True)
        os.makedirs(self.output_config.output_dir, exist_ok=True)

        # Initialize results
        self.results = LyricsControllerResult()

        # Initialize components (with dependency injection)
        self.transcribers = transcribers or self._initialize_transcribers()
        self.lyrics_providers = lyrics_providers or self._initialize_lyrics_providers()
        self.corrector = corrector or LyricsCorrector(cache_dir=self.output_config.cache_dir, logger=self.logger)
        self.output_generator = output_generator or self._initialize_output_generator()

    def _initialize_transcribers(self) -> Dict[str, BaseTranscriber]:
        """Initialize available transcription services."""
        transcribers = {}

        # Add debug logging for config values
        self.logger.debug(f"Initializing transcribers with config: {self.transcriber_config}")
        self.logger.debug(f"Using cache directory for transcribers: {self.output_config.cache_dir}")

        if self.transcriber_config.audioshake_api_token:
            self.logger.debug("Initializing AudioShake transcriber")
            transcribers["audioshake"] = {
                "instance": AudioShakeTranscriber(
                    cache_dir=self.output_config.cache_dir,
                    config=AudioShakeConfig(api_token=self.transcriber_config.audioshake_api_token),
                    logger=self.logger,
                ),
                "priority": 1,  # AudioShake has highest priority
            }
        else:
            self.logger.debug("Skipping AudioShake transcriber - no API token provided")

        if self.transcriber_config.runpod_api_key and self.transcriber_config.whisper_runpod_id:
            self.logger.debug("Initializing Whisper transcriber")
            transcribers["whisper"] = {
                "instance": WhisperTranscriber(
                    cache_dir=self.output_config.cache_dir,
                    config=WhisperConfig(
                        runpod_api_key=self.transcriber_config.runpod_api_key, endpoint_id=self.transcriber_config.whisper_runpod_id
                    ),
                    logger=self.logger,
                ),
                "priority": 2,  # Whisper has lower priority
            }
        else:
            self.logger.debug("Skipping Whisper transcriber - missing runpod_api_key or whisper_runpod_id")

        return transcribers

    def _initialize_lyrics_providers(self) -> Dict[str, BaseLyricsProvider]:
        """Initialize available lyrics providers."""
        providers = {}

        # Create provider config with all necessary parameters
        provider_config = LyricsProviderConfig(
            genius_api_token=self.lyrics_config.genius_api_token,
            spotify_cookie=self.lyrics_config.spotify_cookie,
            cache_dir=self.output_config.cache_dir,
            audio_filepath=self.audio_filepath,
        )

        if provider_config.genius_api_token:
            self.logger.debug("Initializing Genius lyrics provider")
            providers["genius"] = GeniusProvider(config=provider_config, logger=self.logger)
        else:
            self.logger.debug("Skipping Genius provider - no API token provided")

        if provider_config.spotify_cookie:
            self.logger.debug("Initializing Spotify lyrics provider")
            providers["spotify"] = SpotifyProvider(config=provider_config, logger=self.logger)
        else:
            self.logger.debug("Skipping Spotify provider - no cookie provided")

        return providers

    def _initialize_output_generator(self) -> OutputGenerator:
        """Initialize output generation service."""
        return OutputGenerator(config=self.output_config, logger=self.logger)

    def process(self) -> LyricsControllerResult:
        """
        Main processing method that orchestrates the entire workflow.

        Returns:
            LyricsControllerResult containing all outputs and generated files.

        Raises:
            Exception: If a critical error occurs during processing.
        """
        # Step 1: Fetch lyrics if artist and title are provided
        if self.artist and self.title:
            self.fetch_lyrics()

        # Step 2: Run transcription
        self.transcribe()

        # Step 3: Process and correct lyrics
        self.correct_lyrics()

        # Step 4: Generate outputs
        self.generate_outputs()

        self.logger.info("Processing completed successfully")
        return self.results

    def fetch_lyrics(self) -> None:
        """Fetch lyrics from available providers."""
        self.logger.info(f"Fetching lyrics for {self.artist} - {self.title}")

        for name, provider in self.lyrics_providers.items():
            try:
                result = provider.fetch_lyrics(self.artist, self.title)
                if result:
                    self.results.lyrics_results.append(result)
                    self.logger.info(f"Successfully fetched lyrics from {name}")

            except Exception as e:
                self.logger.error(f"Failed to fetch lyrics from {name}: {str(e)}")
                continue

        if not self.results.lyrics_results:
            self.logger.warning("No lyrics found from any source")

    def transcribe(self) -> None:
        """Run transcription using all available transcribers."""
        self.logger.info(f"Starting transcription with providers: {list(self.transcribers.keys())}")

        for name, transcriber_info in self.transcribers.items():
            self.logger.info(f"Running transcription with {name}")
            result = transcriber_info["instance"].transcribe(self.audio_filepath)
            if result:
                # Add the transcriber name and priority to the result
                self.results.transcription_results.append(
                    TranscriptionResult(name=name, priority=transcriber_info["priority"], result=result)
                )
                self.logger.debug(f"Transcription completed for {name}")

        if not self.results.transcription_results:
            self.logger.warning("No successful transcriptions from any provider")

    def correct_lyrics(self) -> None:
        """Run lyrics correction using transcription and internet lyrics."""
        self.logger.info("Starting lyrics correction process")

        # Run correction
        corrected_data = self.corrector.run(
            transcription_results=self.results.transcription_results, lyrics_results=self.results.lyrics_results
        )

        # Store corrected results
        self.results.transcription_corrected = corrected_data
        self.logger.info("Lyrics correction completed")

        # Add human review step
        if self.output_config.enable_review:  # We'll need to add this config option
            from ..review import start_review_server

            self.logger.info("Starting human review process")
            self.results.transcription_corrected = start_review_server(corrected_data)
            self.logger.info("Human review completed")

    def generate_outputs(self) -> None:
        """Generate output files."""
        self.logger.info("Generating output files")

        output_files = self.output_generator.generate_outputs(
            transcription_corrected=self.results.transcription_corrected,
            lyrics_results=self.results.lyrics_results,
            output_prefix=self.output_prefix,
            audio_filepath=self.audio_filepath,
            artist=self.artist,
            title=self.title,
        )

        # Store all output paths in results
        self.results.lrc_filepath = output_files.lrc
        self.results.ass_filepath = output_files.ass
        self.results.video_filepath = output_files.video
        self.results.original_txt = output_files.original_txt
        self.results.corrected_txt = output_files.corrected_txt
        self.results.corrections_json = output_files.corrections_json
        self.results.cdg_filepath = output_files.cdg
        self.results.mp3_filepath = output_files.mp3
        self.results.cdg_zip_filepath = output_files.cdg_zip
