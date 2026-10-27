.PHONY: install download test run reproduce clean

install:
	pip install -r requirements.txt

download:
	python scripts/download_data.py

test:
	pytest tests/ -v --tb=short

run:
	streamlit run app/dashboard.py

reproduce:
	python scripts/reproduce.py

clean:
	rm -rf reports/*.pdf reports/*.json reports/*.png
	rm -rf data/nav_cache/
	rm -rf __pycache__ */__pycache__
