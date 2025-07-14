class CategoryManager:
    def __init__(self):
        self.categories = {}

    def add_category(self, category_name):
        if category_name not in self.categories:
            self.categories[category_name] = []
    
    def add_entry_to_category(self, category_name, entry):
        if category_name in self.categories:
            self.categories[category_name].append(entry)
    
    def get_entries_by_category(self, category_name):
        return self.categories.get(category_name, [])
    
    def get_all_categories(self):
        return list(self.categories.keys())
    
    def remove_category(self, category_name):
        if category_name in self.categories:
            del self.categories[category_name]