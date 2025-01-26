# Chaos Worshiper

The `chaosWorshiper` Python class is a utility for generating JSON metadata files from input files. It processes files in the `input` folder, generates MD5 hashes, determines chaos-based attributes, and saves the results in the `output` folder as JSON files.

## Features
- **Download Files**: Download files from a URL and save them to the `input` folder.
- **Generate MD5 Hashes**: Calculate MD5 hashes for all files in the `input` folder.
- **Chaos Ritual**: Generate chaos-based attributes and stats from MD5 hashes.
- **Save JSON Data**: Save the generated metadata to the `output` folder.
- **Automated Workflow**: Use `magic_function` to process all files in the `input` folder and generate corresponding JSON files.

## Installation

```bash
pip install chaosExtractor
```

## How to Use

### 1. Initialize the Class
Create an instance of the `chaosWorshiper` class:
```python
from chaosExtractor import chaosWorshiper

chaos = chaosWorshiper()
```

### 2. Download Files
Download a file from a URL and save it to the `input` folder:
```python
chaos.download_file('https://example.com/file.txt')
```

### 3. Generate MD5 Hashes
Generate MD5 hashes for all files in the `input` folder:
```python
hashes = chaos.generate_md5_hashes()
print(hashes)
```

### 4. Perform Chaos Ritual
Run the chaos ritual on an MD5 hash to generate stats and metadata:
```python
md5_data = chaos.chaosRitual('aabbccddeeff00112233445566778899')
print(md5_data)
```

### 5. Save JSON Metadata
Save the chaos metadata to the `output` folder:
```python
chaos.save_chaos_json(
    md5_data=md5_data,
    token_id=425,
    name="Chaos token",
    description="Chaos enriched token",
    image_name="425.png",
    custom_attributes={"Origin": "Shadow Realm", "Chaos Rating": 100}
)
```

### 6. Automate the Workflow
Use `summon_chaos` to process all files in the `input` folder and generate corresponding JSON files in the `output` folder:
```python
chaos.summon_chaos()
```

### Folder Structure
- **`input`**: Place your input files here, or use `download_file` to populate this folder.
- **`output`**: The generated JSON metadata files will be saved here.

## Notes
- Ensure the `input` folder exists and contains files before running `magic_function`.
- The JSON output structure can be customized further if needed by modifying the `save_chaos_json` method.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.

