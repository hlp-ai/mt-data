"""Convert XML file of WMT into plain text"""
import argparse
import lxml.etree as ET


def from_xml(xml_file, attr="[@translator='A']"):
    """Convert XML file of WMT into plain text"""
    output_stem = xml_file[:-4]

    pair = xml_file.split(".")[-2]
    src, tgt = pair.split("-")

    tree = ET.parse(xml_file)
    # NOTE: Assumes exactly one translation

    with open(output_stem + "." + src, "w", encoding="utf-8") as ofh:
        for seg in tree.getroot().findall(".//src//seg"):
            print(seg.text, file=ofh)

    with open(output_stem + "." + tgt, "w", encoding="utf-8") as ofh:
        for seg in tree.getroot().findall(".//ref" + attr + "//seg" ):
            print(seg.text, file=ofh)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, required=True, help="input file")
    args = argparser.parse_args()

    corpus_fn = args.input

    from_xml(corpus_fn)
