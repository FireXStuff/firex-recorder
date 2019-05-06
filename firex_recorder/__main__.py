import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--destination',
        help='A destination file to contain the recording of celery events')
    parser.add_argument(
        "--broker",
        help="the broker url")
    args = parser.parse_args()
    print("hello world form " + args.broker + " to " + args.destination)

