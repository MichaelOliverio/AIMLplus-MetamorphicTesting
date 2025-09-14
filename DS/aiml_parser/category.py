class Category:
    def __init__(self, id, intent, argument, dialogue_acts_list, frame, correctedFrame, template):
        self.id = id
        self.intent = intent
        self.argument = argument
        self.dialogue_acts_list = dialogue_acts_list
        self.frame = frame
        self.correctedFrame = correctedFrame
        self.template = template

    def __str__(self):
        return f"Category(id={self.id}, intent={self.intent}, argument={self.argument}, dialogue_acts_list={self.dialogue_acts_list}, frame={self.frame}, correctedFrame={self.correctedFrame}, template={self.template})"