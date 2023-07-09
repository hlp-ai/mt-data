import yaml

from yimt_bitext.utils.filters import EmptyFilter, SameFilter

name2filter = {"EmptyFilter": EmptyFilter,
               "SameFilter": SameFilter}


def load_filters(yml_file):
    with open(yml_file, encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file.read())

        filters = []

        for f in config["filters"]:
            for k, v in f.items():
                filter_name = v["name"]
                filter_params = v["params"]
                if filter_params:
                    filters.append(name2filter[filter_name](**filter_params))
                else:
                    filters.append(name2filter[filter_name]())

        return filters


if __name__ == "__main__":
    fs = load_filters("./filters.yml")
    print(fs)
