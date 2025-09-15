class Category:
    def __init__(self, id, intent, argument, dialogue_acts_list, frame, correctedFrame, template,
                 svg_elements=None, image=None):
        self.id = id
        self.intent = intent
        self.argument = argument
        self.dialogue_acts_list = dialogue_acts_list
        self.frame = frame
        self.correctedFrame = correctedFrame
        self.template = template
        self.svg_elements = svg_elements or []  # lista di dict
        self.image = image  # stringa o None

    def __str__(self):
        return (
            f"Category(id={self.id}, intent={self.intent}, argument={self.argument}, "
            f"dialogue_acts_list={self.dialogue_acts_list}, frame={self.frame}, "
            f"correctedFrame={self.correctedFrame}, template={self.template}, "
            f"svg_elements={self.svg_elements}, image={self.image})"
        )
