import argparse
import glob
import os


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--meta_dir", required=True, help="Directory of metadata file")
    argparser.add_argument("--candidate", type=str, default="./candidates.txt", help="Candidate file path")
    argparser.add_argument("--out_path", type=str, default="./candidate_urls.txt", help="Urls output path")
    args = argparser.parse_args()

    meta_files = glob.glob(os.path.join(args.meta_dir, "*.meta"))

    candidate_netlocs = set()
    with open(args.candidate, encoding="utf-8") as stream:
        for netloc in stream:
            netloc = netloc.strip()
            if netloc not in candidate_netlocs:
                candidate_netlocs.add(netloc)

    urls = set()

    for f in meta_files:
        print("Getting urls from metadata file ", f)
        report_interval = 20000
        total = 0

        with open(f, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                url, host, domain, lang, content_len = parts

                if host in candidate_netlocs or domain in candidate_netlocs:
                    urls.add(url)

                total += 1
                if total % report_interval == 0:
                    print(total)
            print(total)

    with open(args.out_path, "w", encoding="utf-8") as stream:
        for url in urls:
            stream.write(url + "\n")
