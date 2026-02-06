"""
Gestionnaire du panier d'articles

Ce module gere le panier de selection d'articles pour l'export groupe.
Utilise le pattern Singleton pour garantir une instance unique.
"""

from typing import Dict, List, Optional


class CartManager:
    """Gestionnaire singleton du panier d'articles"""

    _instance = None

    def __new__(cls):
        """Pattern Singleton - garantit une seule instance"""
        if cls._instance is None:
            cls._instance = super(CartManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialise le panier (une seule fois)"""
        if self._initialized:
            return
        self._cart_items: Dict[int, Dict] = {}  # {product_id: product_data}
        self._initialized = True

    @classmethod
    def get_instance(cls) -> 'CartManager':
        """
        Retourne l'instance unique du gestionnaire

        Returns:
            Instance du CartManager
        """
        if cls._instance is None:
            cls._instance = CartManager()
        return cls._instance

    def add_to_cart(self, product: Dict) -> bool:
        """
        Ajoute un produit au panier

        Args:
            product: Dictionnaire contenant les donnees du produit
                     Doit contenir au minimum: id, designation, prix_achat

        Returns:
            True si ajout reussi, False si deja present
        """
        product_id = product.get('id')
        if product_id is None:
            return False

        if product_id in self._cart_items:
            return False  # Deja dans le panier

        # Stocker le produit complet
        self._cart_items[product_id] = product.copy()
        return True

    def remove_from_cart(self, product_id: int) -> bool:
        """
        Retire un produit du panier

        Args:
            product_id: ID du produit a retirer

        Returns:
            True si suppression reussie, False si non trouve
        """
        if product_id in self._cart_items:
            del self._cart_items[product_id]
            return True
        return False

    def clear_cart(self) -> None:
        """Vide completement le panier"""
        self._cart_items.clear()

    def get_cart_items(self) -> List[Dict]:
        """
        Retourne la liste des produits dans le panier

        Returns:
            Liste des produits (copies pour eviter modifications)
        """
        return [product.copy() for product in self._cart_items.values()]

    def get_cart_count(self) -> int:
        """
        Retourne le nombre d'articles dans le panier

        Returns:
            Nombre d'articles
        """
        return len(self._cart_items)

    def is_in_cart(self, product_id: int) -> bool:
        """
        Verifie si un produit est deja dans le panier

        Args:
            product_id: ID du produit a verifier

        Returns:
            True si present, False sinon
        """
        return product_id in self._cart_items

    def get_total_ht(self) -> float:
        """
        Calcule le total HT du panier

        Returns:
            Total en euros HT
        """
        total = 0.0
        for product in self._cart_items.values():
            prix = product.get('prix_achat', 0)
            if prix:
                total += float(prix)
        return total

    def get_product_ids(self) -> List[int]:
        """
        Retourne la liste des IDs des produits dans le panier

        Returns:
            Liste des IDs
        """
        return list(self._cart_items.keys())
