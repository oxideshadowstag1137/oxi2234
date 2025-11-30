#!/usr/bin/env python3
"""
prepare_bootloader_data.py

Script to prepare bootloader data for A/B fail-safe bootloader.
This script:
1. Calculates CRC32 of Bank A and Bank B firmware
2. Creates BootloaderData_t structure (12 bytes)
3. Writes to DATA_AREA (0x0800E000)

Usage:
    python prepare_bootloader_data.py --bank-a firmware_a.bin --bank-b firmware_b.bin --active A
    python prepare_bootloader_data.py --bank-a firmware_a.bin --active A  # Only Bank A
"""

import argparse
import struct
import sys
from pathlib import Path

# STM32F103 Hardware CRC32 polynomial
# Reference: STM32F1xx Reference Manual, Section 5.3.3
# Polynomial: 0x04C11DB7 (Ethernet polynomial)
CRC32_POLYNOMIAL = 0x04C11DB7
CRC32_INIT = 0xFFFFFFFF

def stm32_crc32_word(crc, word):
    """Calculate CRC32 for a single 32-bit word (STM32 hardware CRC)"""
    crc ^= word
    for _ in range(32):
        if crc & 0x80000000:
            crc = (crc << 1) ^ CRC32_POLYNOMIAL
        else:
            crc = crc << 1
        crc &= 0xFFFFFFFF
    return crc

def calculate_stm32_crc32(data):
    """
    Calculate CRC32 using STM32 hardware CRC algorithm
    
    Args:
        data: bytes object (must be multiple of 4 bytes)
    
    Returns:
        CRC32 checksum (uint32)
    """
    if len(data) % 4 != 0:
        raise ValueError("Data length must be multiple of 4 bytes")
    
    crc = CRC32_INIT
    
    # Process data as 32-bit words (LITTLE-ENDIAN, matching STM32 memory reads)
    for i in range(0, len(data), 4):
        # STM32 CRC reads memory as little-endian uint32_t
        word = struct.unpack('<I', data[i:i+4])[0]
        crc = stm32_crc32_word(crc, word)
    
    return crc

def pad_to_bank_size(data, bank_size=24*1024):
    """Pad firmware to bank size (24KB) with 0xFF"""
    if len(data) > bank_size:
        raise ValueError(f"Firmware too large: {len(data)} bytes > {bank_size} bytes")
    
    padding = bank_size - len(data)
    return data + b'\xFF' * padding

def create_bootloader_data(active_bank, bank_a_size, bank_b_size, crc_bank_a, crc_bank_b):
    """
    Create BootloaderData_t structure (20 bytes)
    
    typedef struct __attribute__((packed)) {
        uint8_t  active_bank_flag;  // 0xAA = Bank A, 0xBB = Bank B
        uint8_t  padding[3];        // Padding for alignment
        uint32_t bank_a_size;       // Actual size of Bank A firmware
        uint32_t bank_b_size;       // Actual size of Bank B firmware
        uint32_t bank_a_crc32;      // CRC32 of Bank A
        uint32_t bank_b_crc32;      // CRC32 of Bank B
    } BootloaderData_t;
    
    Args:
        active_bank: 'A' or 'B'
        bank_a_size: Actual size of Bank A firmware (uint32)
        bank_b_size: Actual size of Bank B firmware (uint32)
        crc_bank_a: CRC32 of Bank A (uint32)
        crc_bank_b: CRC32 of Bank B (uint32)
    
    Returns:
        20 bytes of data
    """
    if active_bank == 'A':
        flag = 0xAA
    elif active_bank == 'B':
        flag = 0xBB
    else:
        raise ValueError("active_bank must be 'A' or 'B'")
    
    # Pack structure: <B = uint8_t (little-endian)
    #                 3x = 3 bytes padding
    #                 IIII = 4x uint32_t (little-endian)
    data = struct.pack('<B3xIIII', flag, bank_a_size, bank_b_size, crc_bank_a, crc_bank_b)
    
    return data

def main():
    parser = argparse.ArgumentParser(
        description='Prepare bootloader data for A/B fail-safe bootloader'
    )
    parser.add_argument('--bank-a', type=Path, help='Path to Bank A firmware binary')
    parser.add_argument('--bank-b', type=Path, help='Path to Bank B firmware binary')
    parser.add_argument('--active', choices=['A', 'B'], required=True,
                        help='Active bank (A or B)')
    parser.add_argument('--output', type=Path, default='bootloader_data.bin',
                        help='Output file for bootloader data (default: bootloader_data.bin)')
    parser.add_argument('--verbose', action='store_true',
                        help='Verbose output')
    
    args = parser.parse_args()
    
    # Initialize CRC values and sizes
    crc_bank_a = 0xFFFFFFFF
    crc_bank_b = 0xFFFFFFFF
    bank_a_size = 0
    bank_b_size = 0
    
    # Process Bank A
    if args.bank_a:
        if not args.bank_a.exists():
            print(f"Error: Bank A firmware not found: {args.bank_a}", file=sys.stderr)
            return 1
        
        firmware_a = args.bank_a.read_bytes()
        bank_a_size = len(firmware_a)
        if args.verbose:
            print(f"Bank A firmware: {args.bank_a} ({bank_a_size} bytes)")
        
        # Calculate CRC32 on ACTUAL firmware (not padded!)
        crc_bank_a = calculate_stm32_crc32(firmware_a)
        if args.verbose:
            print(f"Bank A CRC32 (on {bank_a_size} bytes): 0x{crc_bank_a:08X}")
    else:
        print("Warning: Bank A firmware not provided, using default values",
              file=sys.stderr)
    
    # Process Bank B
    if args.bank_b:
        if not args.bank_b.exists():
            print(f"Error: Bank B firmware not found: {args.bank_b}", file=sys.stderr)
            return 1
        
        firmware_b = args.bank_b.read_bytes()
        bank_b_size = len(firmware_b)
        if args.verbose:
            print(f"Bank B firmware: {args.bank_b} ({bank_b_size} bytes)")
        
        # Calculate CRC32 on ACTUAL firmware (not padded!)
        crc_bank_b = calculate_stm32_crc32(firmware_b)
        if args.verbose:
            print(f"Bank B CRC32 (on {bank_b_size} bytes): 0x{crc_bank_b:08X}")
    else:
        print("Warning: Bank B firmware not provided, using default values",
              file=sys.stderr)
    
    # Create bootloader data
    bootloader_data = create_bootloader_data(args.active, bank_a_size, bank_b_size, crc_bank_a, crc_bank_b)
    
    # Write to output file
    args.output.write_bytes(bootloader_data)
    
    print(f"\n{'='*60}")
    print(f"Bootloader Data Created Successfully!")
    print(f"{'='*60}")
    print(f"Active Bank:     {args.active}")
    print(f"Bank A Size:     {bank_a_size} bytes")
    print(f"Bank A CRC32:    0x{crc_bank_a:08X}")
    print(f"Bank B Size:     {bank_b_size} bytes")
    print(f"Bank B CRC32:    0x{crc_bank_b:08X}")
    print(f"Output File:     {args.output} (20 bytes)")
    print(f"{'='*60}")
    print(f"\nFlash Instructions:")
    print(f"1. Flash bootloader to 0x08000000")
    if args.bank_a:
        print(f"2. Flash {args.bank_a} to 0x08002000 (Bank A)")
    if args.bank_b:
        print(f"3. Flash {args.bank_b} to 0x08008000 (Bank B)")
    print(f"4. Flash {args.output} to 0x0800E000 (Data Area)")
    print(f"\nExample commands:")
    print(f"st-flash write bootloader.bin 0x08000000")
    if args.bank_a:
        print(f"st-flash write {args.bank_a} 0x08002000")
    if args.bank_b:
        print(f"st-flash write {args.bank_b} 0x08008000")
    print(f"st-flash write {args.output} 0x0800E000")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())
