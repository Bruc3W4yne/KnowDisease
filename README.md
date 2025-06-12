<h1 align="center">KnowDisease Thesis Project for SINTEF</h1>

## Project Prerequisites 
To get the project up and running you need to have set up a Neo4j aura instance at https://neo4j.com/product/auradb/

torch + cuda is also preferred to be set to torchX+cu118 and the CUDA toolkit needs to be installed/setup before running. 
```
git clone https://github.com/Bruc3W4yne/KnowDisease.git
cd KnowDisease
pip install -r requirements.txt (this will take some time due to pytorch)
Install KnowDisease package
pip install -e .
```

Once install finishes you can run the application with: 
```
streamlit run app/Home.py
```

