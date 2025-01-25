# 导入OpenAI Assistants格式的后端线程、消息和矢量库管理器

from DrSai.modules.managers.assistants_manager import AssistantsManager
from DrSai.modules.managers.threads_manager import ThreadsManager
from DrSai.modules.managers.vectorstore_manager import VectorstoresManager
from DrSai.modules.managers.file_manager import FilesManager
from DrSai.modules.managers.vectorstorefile_manager import VectorstorefilesManager
THREADS_MGR = ThreadsManager()
ASSISTANTS_MGR = AssistantsManager()
VECTOR_STORES_MGR = VectorstoresManager()
FILES_MGR = FilesManager()
VECTOR_STORE_FILES_MGR = VectorstorefilesManager()
