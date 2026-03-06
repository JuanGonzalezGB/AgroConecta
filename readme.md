Tkinter is required: for more information check: https://docs.python.org/3/library/tkinter.html Is highly recommended to use a virtual environment, if you don't know how to do that:

    python3 -m venv venv
    source venv/bin/activate

Once you've created and activated the virtual environment you just have to install the requirements:

    pip install -r requirements.txt

Execute the program using:

    python main.py

This version will only run using a remote mongoDB database through the local network. Change /conect/mongoConnection.py to adjust this.

