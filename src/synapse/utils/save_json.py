from synapse.utils.json_cleaner import JSONCleaner

class SaveJson:
    @staticmethod
    def save_json(result, filename: str):
        """
        Generic JSON saver for CrewAI task callbacks.

        Args:
            result: TaskResult object returned by CrewAI.
            filename: Name of the JSON file (e.g. "Suspect_dossiers.json").
        """
        cleaned_json = JSONCleaner.clean_json_content(result.raw)

        with open(filename, "w") as f:
            f.write(cleaned_json)

