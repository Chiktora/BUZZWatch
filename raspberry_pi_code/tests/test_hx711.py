#!/usr/bin/env python3
"""
HX711 Load Cell Calibration and Testing Utility
-----------------------------------------------
This utility helps calibrate and test the HX711 sensor with load cells.
It provides an easy-to-use interface with detailed measurement statistics.

Usage:
  python test_hx711.py               - Run calibration wizard
  python test_hx711.py --test        - Test the scale with existing calibration
  python test_hx711.py --measure     - Take multiple measurements and show statistics
  python test_hx711.py --info        - Show current calibration values
"""

import time
import sys
import os
import statistics
import numpy as np
from BUZZWatch.raspberry_pi_code.hardware_layer.sensors import (
    read_weight, 
    hx, 
    REFERENCE_UNIT, 
    ZERO_OFFSET,
    calibrate_hx711, 
    is_calibrated, 
    cleanup,
    CALIBRATION_FILE
)

def print_header(title=None):
    """Print a header with an optional title"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_separator():
    """Print a separator line"""
    print("-" * 70)

def take_measurements(count=20, delay=0.5, show_raw=True):
    """
    Take multiple measurements and return statistics
    Args:
        count: Number of measurements to take
        delay: Delay between measurements in seconds
        show_raw: Whether to show raw values
    Returns:
        dict: Statistics about the measurements
    """
    if not hx:
        print("ERROR: HX711 sensor not initialized! Check your connections.")
        return None
    
    print(f"Taking {count} measurements with {delay} second intervals...")
    print_separator()
    
    weights = []
    raw_values = []
    
    # Progress bar width
    bar_width = 50
    
    # For larger measurement counts, show batch progress
    batch_size = 10
    total_batches = (count + batch_size - 1) // batch_size
    
    for batch in range(total_batches):
        start_idx = batch * batch_size
        end_idx = min(start_idx + batch_size, count)
        batch_count = end_idx - start_idx
        
        # Show batch progress
        print(f"\rBatch {batch+1}/{total_batches} [", end="")
        
        for i in range(start_idx, end_idx):
            # Get weight reading
            weight = read_weight(return_kg=False)  # Always get in grams for consistency
            
            # Get raw reading if requested
            if show_raw:
                try:
                    readings = hx.get_raw_data(times=3)
                    if readings:
                        raw_avg = sum(readings) / len(readings)
                        raw_values.append(raw_avg)
                except Exception as e:
                    pass
            
            if weight is not None:
                weights.append(weight)
            
            # Show progress within batch
            progress = (i - start_idx + 1) / batch_count
            dots = int(progress * 10)
            print(f"{'•' * dots}{' ' * (10 - dots)}", end="")
            
            time.sleep(delay)
        
        # Complete the batch progress indicator
        print(f"] {end_idx}/{count} readings", end="")
        
        # For high count measurements, show interim statistics
        if count > 50 and len(weights) > 10 and (batch+1) % 2 == 0:
            temp_mean = sum(weights) / len(weights)
            temp_range = max(weights) - min(weights)
            print(f" | Interim mean: {temp_mean:.2f}, range: {temp_range:.2f}")
        else:
            print("")  # Just a newline
    
    print("\nProcessing results...")
    
    # Calculate statistics
    stats = {}
    
    if weights:
        # Enhanced outlier detection for large datasets
        if len(weights) >= 50:
            weights_array = np.array(weights)
            q1, q3 = np.percentile(weights_array, [25, 75])
            iqr = q3 - q1
            
            # Use tighter bounds for larger datasets (1.3 IQR instead of 1.5)
            # This helps filter out more spurious readings in larger samples
            lower_bound = q1 - (1.3 * iqr)
            upper_bound = q3 + (1.3 * iqr)
            
            filtered_weights = [w for w in weights if lower_bound <= w <= upper_bound]
            
            # Only use filtered if we didn't lose too many readings
            if len(filtered_weights) >= len(weights) * 0.75:
                stats['outliers_removed'] = len(weights) - len(filtered_weights)
                print(f"Removed {stats['outliers_removed']} outliers from dataset ({len(filtered_weights)} readings remain)")
                weights = filtered_weights
        
        # Basic stats
        stats['count'] = len(weights)
        stats['min'] = min(weights)
        stats['max'] = max(weights)
        stats['range'] = stats['max'] - stats['min']
        stats['mean'] = sum(weights) / len(weights)
        stats['median'] = statistics.median(weights)
        
        # Advanced stats for larger datasets
        if len(weights) >= 2:
            try:
                stats['stdev'] = statistics.stdev(weights)
                stats['variance'] = statistics.variance(weights)
                
                # Calculate standard error of the mean
                stats['sem'] = stats['stdev'] / np.sqrt(len(weights))
                
                # 95% confidence interval
                stats['ci_95_lower'] = stats['mean'] - 1.96 * stats['sem']
                stats['ci_95_upper'] = stats['mean'] + 1.96 * stats['sem']
            except Exception as e:
                print(f"Error calculating advanced statistics: {e}")
        
        # Calculate stability as coefficient of variation
        if stats['mean'] != 0:
            stats['cv'] = (stats.get('stdev', 0) / stats['mean']) * 100
    
    # Raw value statistics
    if raw_values:
        # Similar outlier detection for raw values
        if len(raw_values) >= 50:
            raw_array = np.array(raw_values)
            q1, q3 = np.percentile(raw_array, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - (1.3 * iqr)
            upper_bound = q3 + (1.3 * iqr)
            filtered_raw = [r for r in raw_values if lower_bound <= r <= upper_bound]
            
            if len(filtered_raw) >= len(raw_values) * 0.75:
                stats['raw_outliers_removed'] = len(raw_values) - len(filtered_raw)
                raw_values = filtered_raw
        
        stats['raw_count'] = len(raw_values)
        stats['raw_min'] = min(raw_values)
        stats['raw_max'] = max(raw_values)
        stats['raw_mean'] = sum(raw_values) / len(raw_values)
        stats['raw_median'] = statistics.median(raw_values)
        
        if len(raw_values) >= 2:
            try:
                stats['raw_stdev'] = statistics.stdev(raw_values)
                stats['raw_cv'] = (stats['raw_stdev'] / stats['raw_mean']) * 100 if stats['raw_mean'] != 0 else 0
            except:
                pass
        
        # Calculate equivalent weight
        if is_calibrated() and REFERENCE_UNIT != 0:
            stats['calculated_weight'] = (stats['raw_mean'] - ZERO_OFFSET) / REFERENCE_UNIT
        
    return stats

def display_measurement_stats(stats):
    """Display measurement statistics in a nice format"""
    if not stats:
        print("No valid measurements were taken.")
        return
    
    print_header("MEASUREMENT STATISTICS")
    
    # Display measurement count
    print(f"Total measurements: {stats['count']}")
    if 'outliers_removed' in stats:
        print(f"Outliers removed: {stats['outliers_removed']} (using 1.3×IQR method)")
    
    print_separator()
    print("WEIGHT MEASUREMENTS:")
    print(f"  Minimum: {stats['min']:.2f}")
    print(f"  Maximum: {stats['max']:.2f}")
    print(f"  Range: {stats['range']:.2f}")
    print(f"  Mean: {stats['mean']:.2f}")
    print(f"  Median: {stats['median']:.2f}")
    
    if 'stdev' in stats:
        print(f"  Standard Deviation: {stats['stdev']:.3f}")
        print(f"  Variance: {stats['variance']:.3f}")
        
        # Show additional precision statistics
        if 'sem' in stats:
            print(f"  Standard Error of Mean: {stats['sem']:.4f}")
        if 'ci_95_lower' in stats and 'ci_95_upper' in stats:
            print(f"  95% Confidence Interval: {stats['ci_95_lower']:.2f} to {stats['ci_95_upper']:.2f}")
    
    if 'cv' in stats:
        print(f"  Coefficient of Variation: {stats['cv']:.2f}%")
        
        # Interpret stability
        if stats['cv'] < 0.5:
            print("  Stability: Exceptional (CV < 0.5%) - Laboratory grade")
        elif stats['cv'] < 1:
            print("  Stability: Excellent (CV < 1%)")
        elif stats['cv'] < 2:
            print("  Stability: Very Good (CV < 2%)")
        elif stats['cv'] < 5:
            print("  Stability: Good (CV < 5%)")
        elif stats['cv'] < 10:
            print("  Stability: Fair (CV < 10%)")
        else:
            print("  Stability: Poor (CV ≥ 10%) - Consider recalibrating")
    
    # Show raw value statistics if available
    if 'raw_count' in stats:
        print_separator()
        print("RAW ADC MEASUREMENTS:")
        print(f"  Raw Mean: {stats['raw_mean']:.2f}")
        print(f"  Raw Median: {stats['raw_median']:.2f}")
        print(f"  Raw Range: {stats['raw_max'] - stats['raw_min']:.2f}")
        
        if 'raw_stdev' in stats:
            print(f"  Raw Standard Deviation: {stats['raw_stdev']:.3f}")
            print(f"  Raw CV: {stats['raw_cv']:.2f}%")
            
        if 'raw_outliers_removed' in stats:
            print(f"  Raw Outliers Removed: {stats['raw_outliers_removed']}")
        
        if 'calculated_weight' in stats:
            print(f"  Calculated Weight from Raw: {stats['calculated_weight']:.2f}")
            print(f"  Difference from Mean: {abs(stats['calculated_weight'] - stats['mean']):.2f}")
            
    # Add a high-precision warning if needed
    if stats['count'] > 100:
        high_precision = True
    else:
        high_precision = False
    
    print_separator()
    
    # Provide interpretation of results based on sample size
    if high_precision:
        if 'cv' in stats and stats['cv'] < 2:
            print("✓ HIGH PRECISION: This measurement used a large sample size with excellent stability.")
            print("  The results are highly reliable for precision calibration.")
        elif 'cv' in stats and stats['cv'] < 5:
            print("✓ GOOD PRECISION: This measurement used a large sample size with good stability.")
            print("  The results are suitable for calibration.")
        else:
            print("⚠ ATTENTION: Despite using a large sample size, the readings show high variation.")
            print("  Consider checking for environmental factors affecting the load cell.")
    else:
        if 'cv' in stats and stats['cv'] < 5:
            print("✓ GOOD MEASUREMENT: The readings show good stability.")
        else:
            print("⚠ VARIABLE MEASUREMENT: The readings show some variability.")
            print("  For higher precision, consider taking more readings (100+).")

def run_calibration_wizard():
    """
    Enhanced interactive wizard for calibrating the HX711 load cells.
    Uses a three-step process with multiple readings for better accuracy:
    1. Empty scale (zero point)
    2. Tare weight (wooden board/platform)
    3. Reference weight on the platform
    """
    global REFERENCE_UNIT, ZERO_OFFSET
    
    print_header("HX711 LOAD CELL CALIBRATION WIZARD (HIGH PRECISION)")
    
    if not hx:
        print("ERROR: HX711 sensor not initialized! Check your connections.")
        return False
    
    print("\nThis wizard will help you calibrate your scale using a three-step process:")
    print("  1. Empty scale (zero point)")
    print("  2. Tare weight (wooden board/platform only)")
    print("  3. Reference weight on the platform")
    print("\nThis calibration uses 150 measurements per step for high precision.")
    
    # Check if already calibrated
    if is_calibrated():
        print("\nYour scale is already calibrated with these values:")
        print(f"  Reference Unit: {REFERENCE_UNIT}")
        print(f"  Zero Offset: {ZERO_OFFSET}")
        
        choice = input("\nDo you want to recalibrate? (y/n): ").strip().lower()
        if choice != 'y':
            print("Calibration cancelled. Keeping existing calibration.")
            return True
    
    # Number of measurements to take for each step
    MEASUREMENTS_COUNT = 150
    
    print_separator()
    print("STEP 1: EMPTY SCALE CALIBRATION")
    print("Make sure your scale is completely empty (no board, no weight).")
    print(f"This step will take approximately {MEASUREMENTS_COUNT * 0.2} seconds.")
    input("Press Enter when the scale is empty and stable...")
    
    # Take measurements with empty scale - using more readings
    print("\nTaking high-precision measurements with empty scale...")
    empty_stats = take_measurements(count=MEASUREMENTS_COUNT, delay=0.2, show_raw=True)
    
    if not empty_stats or 'raw_mean' not in empty_stats:
        print("Failed to get reliable zero readings. Please check connections and try again.")
        return False
    
    # Show stats for empty measurement
    print(f"\nEmpty scale raw value: {empty_stats['raw_mean']:.2f}")
    if 'cv' in empty_stats:
        print(f"Reading stability: {empty_stats['cv']:.2f}% CV")
        if empty_stats['cv'] > 5:
            print("WARNING: High variation in zero readings. Results may be less accurate.")
            print("Try to keep the scale very stable and avoid vibrations/air movement.")
    
    print_separator()
    print("STEP 2: TARE WEIGHT CALIBRATION")
    print("Place ONLY the wooden board/platform on the scale (no reference weight yet).")
    print(f"This step will take approximately {MEASUREMENTS_COUNT * 0.2} seconds.")
    input("Press Enter when the board is placed and stable...")
    
    # Take measurements with tare weight (board)
    print("\nTaking high-precision measurements with tare weight (board)...")
    tare_stats = take_measurements(count=MEASUREMENTS_COUNT, delay=0.2, show_raw=True)
    
    if not tare_stats or 'raw_mean' not in tare_stats:
        print("Failed to get reliable tare readings. Please check connections and try again.")
        return False
    
    # Show stats for tare measurement
    print(f"\nTare weight (board) raw value: {tare_stats['raw_mean']:.2f}")
    print(f"Tare offset from zero: {tare_stats['raw_mean'] - empty_stats['raw_mean']:.2f}")
    
    if 'cv' in tare_stats:
        print(f"Reading stability: {tare_stats['cv']:.2f}% CV")
        if tare_stats['cv'] > 5:
            print("WARNING: High variation in tare readings. Results may be less accurate.")
    
    # Ask for known weight value
    while True:
        try:
            print_separator()
            print("STEP 3: REFERENCE WEIGHT CALIBRATION")
            known_weight = input("Enter your reference weight value (e.g., 1000 for 1kg): ").strip()
            known_weight = float(known_weight)
            if known_weight <= 0:
                print("Weight must be greater than zero.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    
    print(f"\nPlace your {known_weight}g reference weight ON TOP OF THE BOARD.")
    print("Make sure both the board and weight are centered and stable.")
    print(f"This step will take approximately {MEASUREMENTS_COUNT * 0.2} seconds.")
    input("Press Enter when ready...")
    
    # Take measurements with board + reference weight
    print("\nTaking high-precision measurements with reference weight...")
    weight_stats = take_measurements(count=MEASUREMENTS_COUNT, delay=0.2, show_raw=True)
    
    if not weight_stats or 'raw_mean' not in weight_stats:
        print("Failed to get reliable weight readings. Please check connections and try again.")
        return False
    
    # Show stats for weight measurement
    print(f"\nReference weight + board raw value: {weight_stats['raw_mean']:.2f}")
    print(f"Raw value difference from tare: {weight_stats['raw_mean'] - tare_stats['raw_mean']:.2f}")
    
    if 'cv' in weight_stats:
        print(f"Reading stability: {weight_stats['cv']:.2f}% CV")
        if weight_stats['cv'] > 5:
            print("WARNING: High variation in weight readings. Results may be less accurate.")
    
    # Calculate calibration values using tare as the zero point
    value_range = weight_stats['raw_mean'] - tare_stats['raw_mean']
    zero_offset = tare_stats['raw_mean']  # Use tare as zero, not empty
    reference_unit = value_range / known_weight
    
    print_separator()
    print("CALIBRATION RESULTS:")
    print(f"  Empty Raw Value: {empty_stats['raw_mean']:.2f}")
    print(f"  Tare (Board) Raw Value: {tare_stats['raw_mean']:.2f}")
    print(f"  Weight+Board Raw Value: {weight_stats['raw_mean']:.2f}")
    print(f"  Zero Offset (Tare): {zero_offset:.2f}")
    print(f"  Reference Unit: {reference_unit:.6f}")
    print(f"  Raw Value Range (Weight-Tare): {value_range:.2f}")
    
    # Create calibration parameters with more detailed statistics
    calibration_params = {
        'reference_unit': reference_unit,
        'zero_offset': zero_offset,
        'calibration_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'known_weight_used': known_weight,
        'empty_raw': empty_stats['raw_mean'],
        'tare_raw': tare_stats['raw_mean'],
        'weight_raw': weight_stats['raw_mean'],
        'sensitivity': value_range / known_weight,  # Raw counts per unit weight
        'tare_weight_raw_difference': tare_stats['raw_mean'] - empty_stats['raw_mean'],
        'three_step_calibration': True,
        'measurements_per_step': MEASUREMENTS_COUNT,
        'empty_cv': empty_stats.get('cv'),
        'tare_cv': tare_stats.get('cv'),
        'weight_cv': weight_stats.get('cv'),
        'calibration_precision': 'high'
    }
    
    # Save calibration data
    try:
        # Ensure config directory exists
        os.makedirs(os.path.dirname(CALIBRATION_FILE), exist_ok=True)
        
        with open(CALIBRATION_FILE, 'w') as f:
            import json
            json.dump(calibration_params, f, indent=4)
        
        print("\nHigh-precision calibration data saved to:")
        print(f"  {CALIBRATION_FILE}")
        
        # Update global variables (requires restart to take effect fully)
        REFERENCE_UNIT = reference_unit
        ZERO_OFFSET = zero_offset
        
        print("\nNOTE: For the calibration to take full effect, restart your application.")
    except Exception as e:
        print(f"Error saving calibration data: {e}")
        return False
    
    # Test the calibration
    print_separator()
    print("Testing calibration results:")
    
    print("\n1. Testing with ONLY THE BOARD (should read zero):")
    print("   Place only the wooden board on the scale.")
    input("   Press Enter when ready...")
    time.sleep(1)  # Let the scale stabilize
    
    # Test with board (should be zero) - take multiple readings for a more reliable test
    print("   Taking 15 test readings...")
    board_stats = take_measurements(count=15, delay=0.2, show_raw=False)
    if board_stats:
        board_weight = board_stats['mean']
        print(f"   Reading: {board_weight} (should be close to 0 since we're using the board as tare)")
        print(f"   Stability: {board_stats.get('cv', 'N/A')}% CV")
    else:
        print("   Error taking test readings.")
    
    print("\n2. Testing with BOARD + REFERENCE WEIGHT:")
    print(f"   Place the board and your {known_weight}g reference weight on the scale.")
    input("   Press Enter when ready...")
    
    # Test with reference weight - take multiple readings for a more reliable test
    print("   Taking 15 test readings...")
    weight_test_stats = take_measurements(count=15, delay=0.2, show_raw=False)
    
    if weight_test_stats:
        weight = weight_test_stats['mean']
        error = abs(weight - known_weight)
        error_percent = (error / known_weight) * 100 if known_weight != 0 else 0
        
        print(f"   Reading: {weight} (target: {known_weight})")
        print(f"   Error: {error:.2f} ({error_percent:.2f}%)")
        print(f"   Stability: {weight_test_stats.get('cv', 'N/A')}% CV")
        
        # Rate calibration quality
        if error_percent < 0.5:
            print("\nExcellent calibration! Error is less than 0.5%.")
        elif error_percent < 1:
            print("\nVery good calibration! Error is less than 1%.")
        elif error_percent < 3:
            print("\nGood calibration. Error is less than 3%.")
        elif error_percent < 5:
            print("\nAcceptable calibration. Error is less than 5%.")
        else:
            print("\nCalibration may need improvement.")
            print("Try these tips:")
            print("1. Ensure the scale is on a stable, level surface")
            print("2. Verify the reference weight's accuracy")
            print("3. Center all weights carefully on the load cell")
            print("4. Avoid touching or disturbing the scale during readings")
            print("5. Try running the calibration again with more care")
    else:
        print("   Error taking test readings.")
    
    return True

def run_measurements():
    """Run a comprehensive measurement session and display detailed statistics"""
    print_header("HX711 COMPREHENSIVE MEASUREMENTS")
    
    if not hx:
        print("ERROR: HX711 sensor not initialized! Check your connections.")
        return False
    
    # Display calibration status
    if is_calibrated():
        print(f"Scale is calibrated with Reference Unit: {REFERENCE_UNIT}, Zero Offset: {ZERO_OFFSET}")
    else:
        print("WARNING: Scale is not calibrated. Raw values will be shown.")
        print("For accurate weight measurements, run the calibration wizard first.")
    
    print("\nPlace any weight on the scale (or leave empty for zero reading).")
    input("Press Enter when ready to start measurements...")
    
    # Take measurements
    stats = take_measurements(count=30, delay=0.2, show_raw=True)
    
    # Display statistics
    if stats:
        display_measurement_stats(stats)
        return True
    else:
        print("Failed to collect measurements.")
        return False

def test_scale():
    """
    Test the scale with existing calibration.
    Takes continuous readings and displays both weight and raw values.
    """
    print_header("HX711 SCALE TEST")
    
    if not hx:
        print("ERROR: HX711 sensor not initialized! Check your connections.")
        return False
    
    # Check if calibrated
    if is_calibrated():
        print(f"Using calibration values:")
        print(f"  Reference Unit: {REFERENCE_UNIT}")
        print(f"  Zero Offset: {ZERO_OFFSET}")
    else:
        print("WARNING: Scale is not calibrated. Raw values will be shown.")
        print("For accurate weight measurements, run the calibration wizard first.")
    
    # Basic test - continuous readings
    print_separator()
    print("Taking readings every second. Press Ctrl+C to stop.")
    print_separator()
    print("  TIME  |  WEIGHT  |  RAW VALUE  |  CALCULATED WEIGHT")
    print_separator()
    
    start_time = time.time()
    try:
        while True:
            weight = read_weight()
            elapsed = time.time() - start_time
            
            # Try to get raw reading for debugging
            raw_value = "N/A"
            calc_weight = "N/A"
            try:
                if hx:
                    readings = hx.get_raw_data(times=3)
                    if readings:
                        raw_value = sum(readings) / len(readings)
                        # Calculate weight from raw value
                        if is_calibrated() and REFERENCE_UNIT != 0:
                            calc_weight = (raw_value - ZERO_OFFSET) / REFERENCE_UNIT
                            calc_weight = f"{calc_weight:.2f}"
            except:
                pass
                
            print(f"  {elapsed:.1f}s  |  {weight if weight is not None else 'ERROR'}  |  {raw_value}  |  {calc_weight}")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    
    return True

def show_info():
    """
    Display detailed information about the current calibration.
    """
    print_header("HX711 CALIBRATION INFORMATION")
    
    if not hx:
        print("ERROR: HX711 sensor not initialized! Check your connections.")
        return
    
    print(f"Calibration status: {'CALIBRATED' if is_calibrated() else 'NOT CALIBRATED'}")
    
    if is_calibrated():
        print(f"\nCalibration values:")
        print(f"  Reference Unit: {REFERENCE_UNIT}")
        print(f"  Zero Offset: {ZERO_OFFSET}")
        
        print(f"\nCalibration file:")
        print(f"  {CALIBRATION_FILE}")
        
        # Try to read the file to get more info
        try:
            import json
            if os.path.exists(CALIBRATION_FILE):
                with open(CALIBRATION_FILE, 'r') as f:
                    data = json.load(f)
                    print("\nDetailed calibration information:")
                    
                    if 'calibration_date' in data:
                        print(f"  Calibration date: {data['calibration_date']}")
                    
                    if 'known_weight_used' in data:
                        print(f"  Reference weight: {data['known_weight_used']}")
                    
                    if 'sensitivity' in data:
                        print(f"  Sensitivity: {data['sensitivity']:.2f} counts per unit")
                    
                    if 'empty_raw' in data and 'weight_raw' in data:
                        print(f"  Empty raw reading: {data['empty_raw']:.2f}")
                        print(f"  Reference weight raw reading: {data['weight_raw']:.2f}")
                        print(f"  Raw value range: {data['weight_raw'] - data['empty_raw']:.2f}")
        except Exception as e:
            print(f"Error reading calibration file: {e}")
    else:
        print("\nYour scale needs to be calibrated.")
        print("Run this script without arguments to start the calibration wizard.")
    
    # Show hardware configuration
    print_separator()
    print("HARDWARE CONFIGURATION:")
    try:
        print(f"  Channel: {hx.channel}")
        print(f"  Channel A Gain: {hx.channel_a_gain}")
        print(f"  DOUT Pin: {hx._dout}")
        print(f"  PD_SCK Pin: {hx._pd_sck}")
    except:
        print("  Could not retrieve hardware configuration.")

if __name__ == "__main__":
    try:
        # Process command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--test":
                test_scale()
            elif sys.argv[1] == "--measure":
                run_measurements()
            elif sys.argv[1] == "--info":
                show_info()
            else:
                print(f"Unknown argument: {sys.argv[1]}")
                print("Available options: --test, --measure, --info")
        else:
            # By default, run the calibration wizard
            run_calibration_wizard()
        
        # Clean up resources
        cleanup()
        print("\nHX711 resources cleaned up.")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        cleanup()
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        cleanup() 