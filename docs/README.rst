=========
Build Doc
=========

If you'd like to create Sphinx documentation locally, 
follow the steps explained below locally. Tested on Conda 4.6.X

1. Create a conda environment:

.. code-block::

   conda create -n vogue_doc -c bioconda -c conda-forge python=3.6 pip
   conda activate vogue_doc

2. Install Sphinx and extensions:

.. code-block::

   cd docs
   pip install -r requirements.txt -r ../requirements-dev.txt -r ../requirements.txt 

3. Build docs:

.. code-block::

   sphinx-apidoc -o source/ ../vogue
   sphinx-build -T -E -b html -d _build/doctrees-readthedocs -D language=en . _build/html

4. View docs (\ ``open`` or similar command from your OS):

.. code-block::

   open _build/html/index.html

