from orloWeb.config import config
import orloclient


orlo = orloclient.Orlo(
    uri=config.get('orlo', 'uri')
)
