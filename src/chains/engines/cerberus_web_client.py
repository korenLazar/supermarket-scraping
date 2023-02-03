from abc import abstractmethod



from src.supermarket_chain import SupermarketChain


class CerberusWebClient(SupermarketChain):
    
    @property
    @abstractmethod
    def username(self):
        pass

   