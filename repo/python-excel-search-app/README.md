# Python Excel Search Application

This project is a Python application that provides a graphical user interface (GUI) for searching and filtering data imported from Excel files. Users can categorize and group entries based on defined criteria while maintaining the original table structure. The application also allows users to copy selected entries to a new section.

## Features

- Import data from Excel files.
- Search for specific text within the data.
- Filter and group entries based on user-defined categories.
- Maintain the original structure of the Excel table.
- Copy selected entries to a new section for further use.

## Project Structure

```
python-excel-search-app
├── src
│   ├── main.py          # Entry point of the application
│   ├── gui.py           # GUI implementation
│   ├── excel_utils.py   # Utilities for Excel file handling
│   ├── filters.py       # Functions for filtering data
│   └── categories.py     # Management of categories for grouping
├── requirements.txt      # List of dependencies
└── README.md             # Project documentation
```

## Installation

To run this application, you need to install the required dependencies. You can do this by running:

```
pip install -r requirements.txt
```

## Usage

1. Run the application by executing the following command:

   ```
   python src/main.py
   ```

2. Use the GUI to load an Excel file.
3. Enter the text you want to search for in the provided search field.
4. Apply filters to narrow down the results based on your criteria.
5. Group entries using the defined categories.
6. Select entries you wish to copy and use the copy functionality to move them to a new section.

## Dependencies

This project requires the following Python libraries:

- Tkinter or PyQt (for GUI development)
- pandas or openpyxl (for handling Excel files)

Make sure to check the `requirements.txt` file for the specific versions needed.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.