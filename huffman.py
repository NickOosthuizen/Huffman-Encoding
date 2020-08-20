from decoder import Decoder
from encoder import Encoder
import argparse

def encode_file(file_name):
    encoder_object = Encoder()
    encoder_object.encode_and_write_file(file_name)

def decode_file(file_name):
    decoder_object = Decoder()
    decoder_object.decode_and_write_file(file_name)

def main():
    usage_msg = "huffman.py [option] [file] Encode or decode a file using Huffman Encoding"
    parser = argparse.ArgumentParser(description = usage_msg)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--encode", "-e",  action="store_true", help="encode file")
    group.add_argument("--decode", "-d", action="store_true", help="decode file")
    parser.add_argument("file_name", help="file to be processed")
    args = parser.parse_args()

    if args.encode:
        encode_file(args.file_name)
    elif args.decode:
        decode_file(args.file_name)
    else:
        print("Encode or decode argument required, enter 'huffman.py -h' for options")

if __name__ == '__main__':
    main()