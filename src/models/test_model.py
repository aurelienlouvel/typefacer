import lightning as L

class TypeFacerModel(L.LightningModule):
    def __init__(self):
        super().__init__()
        self.save_hyperparameters()

    def forward(self, x):
        # Pour l'instant, juste un pass-through
        return x

if __name__ == "__main__":
    # Test simple
    model = TypeFacerModel()
    print("Model initialized successfully!")
    print(f"Using Lightning version: {L.__version__}")
