"""Generate migrations for partner packages."""

import importlib
from typing import List, Tuple

from aibaba_ai_core.documents import BaseDocumentCompressor, BaseDocumentTransformer
from aibaba_ai_core.embeddings import Embeddings
from aibaba_ai_core.language_models import BaseLanguageModel
from aibaba_ai_core.retrievers import BaseRetriever
from aibaba_ai_core.vectorstores import VectorStore

from aibaba_ai_cli.namespaces.migrate.generate.utils import (
    COMMUNITY_PKG,
    find_subclasses_in_module,
    list_classes_by_package,
    list_init_imports_by_package,
)

# PUBLIC API


def get_migrations_for_partner_package(pkg_name: str) -> List[Tuple[str, str]]:
    """Generate migrations from community package to partner package.

    This code works

    Args:
        pkg_name (str): The name of the partner package.

    Returns:
        List of 2-tuples containing old and new import paths.
    """
    package = importlib.import_module(pkg_name)
    classes_ = find_subclasses_in_module(
        package,
        [
            BaseLanguageModel,
            Embeddings,
            BaseRetriever,
            VectorStore,
            BaseDocumentTransformer,
            BaseDocumentCompressor,
        ],
    )
    community_classes = list_classes_by_package(str(COMMUNITY_PKG))
    imports_for_pkg = list_init_imports_by_package(str(COMMUNITY_PKG))

    old_paths = community_classes + imports_for_pkg

    migrations = [
        (f"{module}.{item}", f"{pkg_name}.{item}")
        for module, item in old_paths
        if item in classes_
    ]
    return migrations
