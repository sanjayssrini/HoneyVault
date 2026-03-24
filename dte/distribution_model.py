import json
import random
from collections import Counter

class VaultDistribution:

    def __init__(self, dataset_path):
        try:
            with open(dataset_path) as f:
                raw = f.read().strip()
                if not raw:
                    raise ValueError("Dataset is empty.")
                self.data = json.loads(raw)
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Dataset file not found: {dataset_path}"
            )
        except json.JSONDecodeError:
            raise ValueError(
                f"Dataset file is not valid JSON: {dataset_path}"
            )

        if not isinstance(self.data, list) or len(self.data) == 0:
            raise ValueError(
                "Dataset must be a non-empty list of vault objects."
            )

        required_keys = {"email", "password", "notes"}
        for i, item in enumerate(self.data):
            if not required_keys.issubset(item.keys()):
                raise ValueError(
                    f"Entry {i} missing required keys: {required_keys}"
                )

        self.email_domains = Counter()
        self.password_lengths = Counter()
        self.note_types = Counter()

        self._fit()

    def _fit(self):
        for v in self.data:
            domain = v["email"].split("@")[1]
            self.email_domains[domain] += 1
            self.password_lengths[len(v["password"])] += 1
            self.note_types[v["notes"]] += 1

    def sample_email(self):
        domain = random.choices(
            list(self.email_domains.keys()),
            weights=self.email_domains.values()
        )[0]
        user = f"user{random.randint(100,999)}"
        return f"{user}@{domain}"

    def sample_password(self):
        length = random.choices(
            list(self.password_lengths.keys()),
            weights=self.password_lengths.values()
        )[0]
        chars = "AaBbCcDd123!@"
        return "".join(random.choice(chars) for _ in range(length))

    def sample_note(self):
        return random.choices(
            list(self.note_types.keys()),
            weights=self.note_types.values()
        )[0]
