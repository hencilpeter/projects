import csv


class DictUtil:
    @staticmethod
    def write_dict_to_csv(_dict, _csv_file_name):
        with open(_csv_file_name, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=_dict.keys())
            writer.writeheader()
            writer.writerow(_dict)

    @staticmethod
    def read_dict_from_csv(_csv_file_name):
        # read csv file to a list of dictionaries
        with open(_csv_file_name, 'r') as file:
            csv_reader = csv.DictReader(file)
            dictobj = next(csv_reader)

        for key in dictobj.keys():
            dictobj[key] = dictobj[key].strip('][').split(', ')
            dictobj[key] = [item.strip("'") for item in dictobj[key]]

        return dictobj
