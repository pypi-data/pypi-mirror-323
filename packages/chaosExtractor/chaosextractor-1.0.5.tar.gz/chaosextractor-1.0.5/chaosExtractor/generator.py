import os
import hashlib
import requests
import json

class chaosWorshiper:
    def __init__(self, input_folder='input', output_folder='output'):
        self.input_folder = input_folder
        self.output_folder = output_folder
        os.makedirs(self.input_folder, exist_ok=True)
        os.makedirs(self.output_folder, exist_ok=True)

    def save_chaos_json(self, md5_data, token_id, name, description, image_name, custom_attributes=None):
        """
        Saves the final JSON data to the output folder based on the given MD5 data and other details.

        :param md5_data: dict - The MD5 data generated from the chaosRitual function.
        :param token_id: int - The token ID for the output JSON.
        :param name: str - The name for the output JSON.
        :param description: str - The description for the output JSON.
        :param image_name: str - The name of the image file (e.g., "425.png").
        :param custom_attributes: dict - A dictionary of custom attributes to include in the JSON file (optional).
        :return: str - The file path of the saved JSON.
        """
        # Prepare JSON data
        json_data = {
            "tokenId": token_id,
            "name": name,
            "description": description,
            "image": image_name,
            "attributes": [
                {"trait_type": "Charisma", "value": md5_data["stats"]["charisma"], "display_type": "number", "max_value":45 },
                {"trait_type": "Charisma Tier", "value": md5_data["stats"]["charisma_tier"]},
                {"trait_type": "Humour", "value": md5_data["stats"]["humour"], "display_type": "number", "max_value":45},
                {"trait_type": "Humour Tier", "value": md5_data["stats"]["humour_tier"]},
                {"trait_type": "Agility", "value": md5_data["stats"]["agility"], "display_type": "number", "max_value":45},
                {"trait_type": "Agility Tier", "value": md5_data["stats"]["agility_tier"]},
                {"trait_type": "Observance", "value": md5_data["stats"]["observance"], "display_type": "number", "max_value":45},
                {"trait_type": "Observance Tier", "value": md5_data["stats"]["observance_tier"]},
                {"trait_type": "Strength", "value": md5_data["stats"]["strength"], "display_type": "number", "max_value":45},
                {"trait_type": "Strength Tier", "value": md5_data["stats"]["strength_tier"]},
                {"trait_type": "Class Name", "value": md5_data["class_name"]},
                {"trait_type": "Specialization", "value": md5_data["specialization"]},
                {"trait_type": "Role", "value": md5_data["role"]},
                {"trait_type": "Chaos Metric", "value": md5_data["chaos_metric"], "display_type": "number", "max_value":225}
            ]
        }

        # Add custom attributes if provided
        if custom_attributes:
            for key, value in custom_attributes.items():
                json_data["attributes"].append({"trait_type": key, "value": value})

        # Save to output folder
        output_path = os.path.join(self.output_folder, f"{token_id}.json")
        with open(output_path, "w") as json_file:
            json.dump(json_data, json_file, indent=4)
        print(f"JSON saved to: {output_path}")
        return output_path

    def download_file(self, url):
        """
        Downloads a file from the given URL and saves it to the 'input' folder.

        :param url: str - URL of the file to download.
        :return: str - Path to the downloaded file.
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            # Determine the new filename based on the number of files in the directory
            file_count = len(os.listdir(self.input_folder)) + 1
            filename = f"{file_count}"
            filepath = os.path.join(self.input_folder, filename)

            # Save the file
            with open(filepath, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"File downloaded and saved as: {filepath}")
            return filepath
        except requests.RequestException as e:
            print(f"Error downloading file: {e}")
            return None

    def generate_md5_hashes(self):
        """
        Generates MD5 hashes for all files in the 'input' folder.

        :return: dict - A dictionary with file names (without extension) as keys and their MD5 hashes as values.
        """
        hashes = {}
        try:
            for filename in os.listdir(self.input_folder):
                filepath = os.path.join(self.input_folder, filename)

                if os.path.isfile(filepath):
                    # Calculate MD5 hash
                    md5_hash = hashlib.md5()
                    with open(filepath, 'rb') as file:
                        while chunk := file.read(8192):
                            md5_hash.update(chunk)

                    # Store the hash with filename without extension
                    file_base_name = os.path.splitext(filename)[0]
                    hashes[file_base_name] = md5_hash.hexdigest()

            print("MD5 hashes generated:", hashes)
            return hashes
        except Exception as e:
            print(f"Error generating MD5 hashes: {e}")
            return {}

    def generate_md5_hash(self, filepath):
        """
        Generates MD5 hash for specific file.

        :return: str - MD5 hash of file.
        """

        try:
            if os.path.isfile(filepath):
                # Calculate MD5 hash
                md5_hash = hashlib.md5()
                with open(filepath, 'rb') as file:
                    while chunk := file.read(8192):
                        md5_hash.update(chunk)

                hash_ret = md5_hash.hexdigest()

                print("MD5 hash generated:", hash_ret)
                return hash_ret
            else:
                print(f"{filepath} not found or not a file")
        except Exception as e:
            print(f"Error generating MD5 hash: {e}")
            return {}

    def _char_to_number(self, char):
        """
        Converts a character to a number: digits remain as they are, and letters are mapped to 10-35 (a=10, b=11, ..., z=35).

        :param char: str - The character to convert.
        :return: int - The corresponding number.
        """
        if char.isdigit():
            return int(char)
        return ord(char.lower()) - ord('a') + 10

    def _extract_stat(self, md5, start_index, role):
        """
        Extracts and calculates a stat based on the role-specific algorithm.

        :param md5: str - The MD5 hash string.
        :param start_index: int - The starting index for the stat in the hash.
        :param role: str - The role to determine which algorithm to use ("knight", "adept", "leader", "acolyte").
        :return: int - The calculated stat value.
        """
        values = [self._char_to_number(md5[i]) for i in range(start_index, start_index + 5)]

        if role == "knight":
            return ((values[0] // 2) + values[1]) * 2
        elif role == "adept":
            return ((values[1] // 2) + values[0]) * 2
        elif role == "leader":
            return ((values[0] + values[1]) // 2) * 3
        elif role == "acolyte":
            base_stat = sum(values[:2]) // 2
            bonus = values[4]
            return base_stat + bonus
        elif role == 'messiah':
            return values[0]
        else:
            return values[4]

    def _get_stat_tier(self, stat):
        """
        Determines the tier for a given stat.

        :param stat: int - The stat value.
        :return: str - The corresponding tier name.
        """
        if stat <= 15:
            return 'common'
        elif 16 <= stat <= 29:
            return 'trained'
        elif 30 <= stat <= 38:
            return 'talented'
        elif 39 <= stat <= 43:
            return 'genius'
        elif 44 <= stat <= 45:
            return 'divine'
        else:
            return 'undefined'

    def chaosRitual(self, md5, role = None):
        """
        Determines which chaos function to call based on the first three symbols of the MD5 string.

        :param role: str - to override role as test
        :param md5: str - The MD5 string to evaluate.
        :return: dict - The JSON object returned by the called function.
        """
        if len(md5) != 32:
            raise ValueError("This is not md5 string")

        first, second, third = md5[0], md5[1], md5[2]
        if role is None:
            if first == second == third:
                role = 'messiah'
            elif first == second:
                role ='adept'
            elif second == third:
                role = 'leader'
            elif first == third:
                role = 'knight'
            else:
                role = 'acolyte'

        charisma = self._extract_stat(md5, 3, role=role)
        humour = self._extract_stat(md5, 8, role=role)
        agility = self._extract_stat(md5, 13, role=role)
        observance = self._extract_stat(md5, 18, role=role)
        strength = self._extract_stat(md5, 23, role=role)
        if role=='messiah':
            charisma_n = int((charisma + humour + agility + observance + strength)/3) + self._extract_stat(md5, 3, role='bonus')+5
            humour_n = int((charisma + humour + agility + observance + strength) / 3)  + self._extract_stat(md5, 8, role='bonus')+5
            agility_n = int((charisma + humour + agility + observance + strength) / 3) + self._extract_stat(md5, 13, role='bonus')+5
            observance_n = int((charisma + humour + agility + observance + strength) / 3) + self._extract_stat(md5, 18, role='bonus')+5
            strength_n = int((charisma + humour + agility + observance + strength) / 3) + self._extract_stat(md5, 23, role='bonus')+5
            charisma=charisma_n
            humour=humour_n
            agility=agility_n
            observance=observance_n
            strength=strength_n
        stats = {
            "charisma": charisma,
            "charisma_tier": self._get_stat_tier(charisma),
            "humour": humour,
            "humour_tier": self._get_stat_tier(humour),
            "agility": agility,
            "agility_tier": self._get_stat_tier(agility),
            "observance": observance,
            "observance_tier": self._get_stat_tier(observance),
            "strength": strength,
            "strength_tier": self._get_stat_tier(strength)
        }

        total_score = charisma + humour + agility + observance + strength

        return {
            "role": f'Chaos {role}',
            "md5": md5,
            "stats": stats,
            "class_name": self._generate_class_name(total_score),
            "chaos_metric": total_score,
            "specialization": self._generate_funny_specialization_with_adjectives(stats)
        }

    def _generate_class_name(self, total_score):
        """
        Generates a class name based on total stats.

        :param stats: dict - A dictionary of stats.
        :return: str - The generated class name.
        """

        if total_score <= 75:
            return "Novice of Chaos"
        elif 76 <= total_score <= 120:
            return "Wanderer of Shadows"
        elif 121 <= total_score <= 165:
            return "Master of Discord"
        elif 166 <= total_score <= 200:
            return "Archon of Anarchy"
        else:
            return "Chaos Overlord"

    def _generate_funny_specialization_with_adjectives(self, stats):
        """
        Generates a funny and unique specialization based on the highest stat(s), their tiers, and an adjective.

        :param stats: dict - A dictionary containing stats and their tiers, e.g.:
                     {
                         "charisma": 25,
                         "charisma_tier": "trained",
                         "humour": 30,
                         "humour_tier": "talented",
                         ...
                     }
        :return: str - A funny and unique specialization name based on the stats distribution and tiers.
        """
        # Adjectives based on tiers
        tier_adjectives = {
            "common": "Humble",
            "trained": "Skilled",
            "talented": "Brilliant",
            "genius": "Legendary",
            "divine": "Godlike"
        }

        # Find the highest stat value
        max_value = max(stats[stat] for stat in ["charisma", "humour", "agility", "observance", "strength"])

        # Collect stats with the highest value
        highest_stats = [
            stat for stat in ["charisma", "humour", "agility", "observance", "strength"]
            if stats[stat] == max_value
        ]

        # Determine the adjective based on the tier of the highest stats
        tier = stats[f"{highest_stats[0]}_tier"]  # Since all tied stats share the same tier
        adjective = tier_adjectives.get(tier, "Mysterious")

        # Predefined combinations of stats and their funny names
        funny_names = {
            frozenset(["charisma"]): "Charming Luminary",
            frozenset(["humour"]): "Hilarious Trickster",
            frozenset(["agility"]): "Graceful Blur",
            frozenset(["observance"]): "All-Seeing Owl",
            frozenset(["strength"]): "Mighty Juggernaut",
            frozenset(["charisma", "humour"]): "Witty Charmer",
            frozenset(["charisma", "agility"]): "Nimble Diplomat",
            frozenset(["charisma", "observance"]): "Perceptive Orator",
            frozenset(["charisma", "strength"]): "Charismatic Titan",
            frozenset(["humour", "agility"]): "Acrobat of Wit",
            frozenset(["humour", "observance"]): "Insightful Joker",
            frozenset(["humour", "strength"]): "Laughing Warrior",
            frozenset(["agility", "observance"]): "Stealthy Seer",
            frozenset(["agility", "strength"]): "Agile Powerhouse",
            frozenset(["observance", "strength"]): "Watchful Titan",
            frozenset(["charisma", "humour", "agility"]): "Graceful Entertainer",
            frozenset(["charisma", "humour", "observance"]): "Insightful Showman",
            frozenset(["charisma", "humour", "strength"]): "Powerful Performer",
            frozenset(["charisma", "agility", "observance"]): "Diplomatic Shadow",
            frozenset(["charisma", "agility", "strength"]): "Charming Powerhouse",
            frozenset(["charisma", "observance", "strength"]): "All-Seeing Titan",
            frozenset(["humour", "agility", "observance"]): "Witty Acrobat",
            frozenset(["humour", "agility", "strength"]): "Laughing Powerhouse",
            frozenset(["humour", "observance", "strength"]): "Wise Warrior",
            frozenset(["agility", "observance", "strength"]): "Nimble Protector",
            frozenset(["charisma", "humour", "agility", "observance"]): "Multifaceted Genius",
            frozenset(["charisma", "humour", "agility", "strength"]): "Dynamic Performer",
            frozenset(["charisma", "humour", "observance", "strength"]): "Visionary Powerhouse",
            frozenset(["charisma", "agility", "observance", "strength"]): "All-Terrain Leader",
            frozenset(["humour", "agility", "observance", "strength"]): "Agile Jester",
            frozenset(["charisma", "humour", "agility", "observance", "strength"]): "Chaos Supreme"
        }

        # Get the combination name, or return a default if not found
        base_name = funny_names.get(frozenset(highest_stats), "Undefined Enigma")
        return f"{adjective} {base_name}"

    def summon_chaos(self, description="An unique c.h.a.o.s. entity spawned from the depths of void."):
        """
        Processes all files in the input folder, generates MD5 hashes, and creates corresponding JSON files
        with the same names in the output folder.

        :return: None
        """
        # Generate MD5 hashes for all files in the input folder
        hashes = self.generate_md5_hashes()

        for file_name, md5 in hashes.items():
            try:
                # Perform chaos ritual to generate stats and data
                md5_data = self.chaosRitual(md5)

                # Prepare attributes for the JSON
                token_id = int(file_name)  # Assuming filenames are numerical
                name = f"Chaos Token {token_id}"

                image_name = f"{file_name}.png"  # Example image name, replace as needed

                # Save the JSON data to the output folder
                self.save_chaos_json(
                    md5_data=md5_data,
                    token_id=token_id,
                    name=name,
                    description=description,
                    image_name=image_name
                )
            except Exception as e:
                print(f"Error processing file {file_name}: {e}")

        print("All files processed and JSON files created.")