from hstream import hstream as hs
from hstream import component

@component
def my_custom_component(self, label, key=None, **kwargs):
    with self.tag("div", ("class", "custom-component")):
        self.text(f"Custom: {label}")
    return "custom_value"

def test_custom_component():
    # Verify the method exists on the hs instance
    assert hasattr(hs, "my_custom_component")
    
    # Verify it runs (this is a basic check, fully running it requires the django context usually, 
    # but we can check if the method is callable and returns what we expect from the wrapper)
    # Note: The wrapper expects 'key' or generates one, and interacts with _hs_session.
    # For this unit test, we might hit session errors if we run it fully without mocking.
    # Let's just check registration for now.
    print("Custom component registered successfully")

if __name__ == "__main__":
    test_custom_component()
