
# hyperspectral_processor.py - Hyperspectral Image Processing Module
import numpy as np
import cv2
from PIL import Image
import logging
from typing import Dict, List, Tuple, Optional
import json
import os

logger = logging.getLogger(__name__)

class HyperspectralProcessor:
    def __init__(self):
        self.supported_formats = ['.raw', '.hdr', '.img', '.bil', '.bip', '.bsq', '.tif', '.tiff']
        self.common_wavelengths = np.arange(400, 1000, 5)  # 400-1000nm with 5nm intervals

        # Spectral indices parameters
        self.indices_params = {
            'ndvi': {'red': 670, 'nir': 800},
            'evi': {'blue': 450, 'red': 670, 'nir': 800},
            'savi': {'red': 670, 'nir': 800, 'l': 0.5},
            'ari': {'green': 550, 'rededge': 700},
            'pssr': {'nir': 800, 'red': 670}
        }

    def load_and_preprocess(self, file_path: str) -> Dict:
        try:
            logger.info(f"Loading hyperspectral image: {file_path}")

            # Determine file format and load accordingly
            file_ext = os.path.splitext(file_path)[1].lower()

            if file_ext in ['.raw', '.hdr']:
                data = self._load_envi_format(file_path)
            elif file_ext in ['.tif', '.tiff']:
                data = self._load_tiff_format(file_path)
            else:
                # Try generic loading
                data = self._load_generic_format(file_path)

            # Preprocess the data
            processed_data = self._preprocess_hyperspectral_data(data)

            return {
                'data': processed_data['corrected_reflectance'],
                'wavelengths': processed_data['wavelengths'],
                'metadata': processed_data['metadata'],
                'shape': processed_data['corrected_reflectance'].shape,
                'processing_info': processed_data['processing_info']
            }

        except Exception as e:
            logger.error(f"Error loading hyperspectral image: {str(e)}")
            raise

    def _simulate_hyperspectral_data(self, height: int = 512, width: int = 512) -> Dict:
        logger.info("Generating simulated hyperspectral data for testing")

        wavelengths = np.arange(400, 1000, 5)  # 400-1000nm, 5nm intervals
        n_bands = len(wavelengths)

        # Create base image with different crop and soil regions
        base_image = np.zeros((height, width, n_bands))

        # Generate realistic vegetation spectra
        for i in range(height):
            for j in range(width):
                # Create different regions with different spectral signatures
                if (i + j) % 20 < 10:  # Vegetation region
                    spectrum = self._generate_vegetation_spectrum(wavelengths)
                    # Add some variability for health simulation
                    health_factor = 0.8 + 0.4 * np.random.random()
                    spectrum = spectrum * health_factor
                else:  # Soil region
                    spectrum = self._generate_soil_spectrum(wavelengths)

                # Add noise
                noise = np.random.normal(0, 0.02, n_bands)
                spectrum = spectrum + noise
                spectrum = np.clip(spectrum, 0, 1)

                base_image[i, j, :] = spectrum

        metadata = {
            'format': 'simulated',
            'description': 'Simulated hyperspectral agricultural data',
            'bands': n_bands,
            'wavelength_range': '400-1000nm',
            'spatial_resolution': '1m',
            'spectral_resolution': '5nm'
        }

        return {
            'data': base_image,
            'wavelengths': wavelengths,
            'metadata': metadata
        }

    def _generate_vegetation_spectrum(self, wavelengths: np.ndarray) -> np.ndarray:
        spectrum = np.zeros_like(wavelengths, dtype=float)

        for i, wl in enumerate(wavelengths):
            if wl < 500:  # Blue region - low reflectance
                spectrum[i] = 0.04 + 0.02 * np.random.random()
            elif wl < 600:  # Green region - moderate reflectance
                spectrum[i] = 0.08 + 0.04 * np.random.random()
            elif wl < 700:  # Red region - low reflectance (chlorophyll absorption)
                spectrum[i] = 0.04 + 0.02 * np.random.random()
            elif wl < 750:  # Red edge - rapid increase
                spectrum[i] = 0.1 + 0.6 * ((wl - 700) / 50)
            else:  # NIR region - high reflectance
                spectrum[i] = 0.7 + 0.2 * np.random.random()

        return spectrum
