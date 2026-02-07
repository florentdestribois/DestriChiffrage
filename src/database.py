"""
DestriChiffrage - Module Base de Donnees
=========================================
Gestion de la base de donnees SQLite pour le chiffrage et approvisionnement
"""

import sqlite3
import csv
import os
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Any
from config import get_config

class Database:
    """Classe de gestion de la base de donnees SQLite"""

    def __init__(self, db_path: str = None, data_dir: str = None):
        """
        Initialise la connexion a la base de donnees

        Args:
            db_path: Chemin vers le fichier de base de donnees (optionnel)
            data_dir: Dossier data à utiliser (optionnel, sinon lit la config)
        """
        # Charger la configuration globale
        config = get_config()

        # Déterminer le data_dir à utiliser
        if data_dir is None:
            data_dir = config.get_data_dir()

        # Normaliser et stocker le data_dir
        self.data_dir = os.path.normpath(os.path.abspath(data_dir))

        # Créer le dossier data s'il n'existe pas
        os.makedirs(self.data_dir, exist_ok=True)

        # Le chemin de la base est toujours {data_dir}/catalogue.db
        if db_path is None:
            db_path = os.path.join(self.data_dir, "catalogue.db")

        # Créer le dossier si nécessaire
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        # Assurer l'encodage UTF-8
        self.conn.execute("PRAGMA encoding = 'UTF-8'")
        self.conn.text_factory = str  # Forcer les textes en str (unicode en Python 3)
        self._create_tables()

    def _create_tables(self):
        """Cree les tables si elles n'existent pas"""
        cursor = self.conn.cursor()

        # Table des produits
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                categorie TEXT NOT NULL,
                sous_categorie TEXT,
                designation TEXT NOT NULL,
                dimensions TEXT,
                hauteur INTEGER,
                largeur INTEGER,
                prix_achat REAL DEFAULT 0,
                reference TEXT,
                fournisseur TEXT,
                chantier TEXT,
                notes TEXT,
                fiche_technique TEXT,
                actif INTEGER DEFAULT 1,
                date_ajout TEXT DEFAULT CURRENT_TIMESTAMP,
                date_modification TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Migration: ajouter colonnes hauteur/largeur si elles n'existent pas
        try:
            cursor.execute("ALTER TABLE produits ADD COLUMN hauteur INTEGER")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE produits ADD COLUMN largeur INTEGER")
        except:
            pass
        # Migration: ajouter colonne chantier si elle n'existe pas
        try:
            cursor.execute("ALTER TABLE produits ADD COLUMN chantier TEXT")
        except:
            pass
        # Migration: ajouter colonne fiche_technique si elle n'existe pas
        try:
            cursor.execute("ALTER TABLE produits ADD COLUMN fiche_technique TEXT")
        except:
            pass
        # Migration: ajouter colonne devis_fournisseur si elle n'existe pas
        try:
            cursor.execute("ALTER TABLE produits ADD COLUMN devis_fournisseur TEXT")
        except:
            pass
        # Migration: ajouter colonnes sous_categorie_2 et sous_categorie_3 si elles n'existent pas
        try:
            cursor.execute("ALTER TABLE produits ADD COLUMN sous_categorie_2 TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE produits ADD COLUMN sous_categorie_3 TEXT")
        except:
            pass
        # Migration v1.3.0: ajouter colonne description dans produits
        try:
            cursor.execute("ALTER TABLE produits ADD COLUMN description TEXT")
        except:
            pass

        # Migration v1.3.0: ajouter colonnes nom_client et type_marche dans chantiers
        try:
            cursor.execute("ALTER TABLE chantiers ADD COLUMN nom_client TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE chantiers ADD COLUMN type_marche TEXT DEFAULT 'PUBLIC'")
        except:
            pass

        # Migration v1.3.0: ajouter colonnes description et taux_tva dans prix_marche
        try:
            cursor.execute("ALTER TABLE prix_marche ADD COLUMN description TEXT")
        except:
            pass
        try:
            cursor.execute("ALTER TABLE prix_marche ADD COLUMN taux_tva REAL DEFAULT 20")
        except:
            pass

        # Migration v1.3.5: ajouter colonne presentation dans prix_marche
        try:
            cursor.execute("ALTER TABLE prix_marche ADD COLUMN presentation TEXT")
        except:
            pass

        # Table des categories
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT UNIQUE NOT NULL,
                description TEXT,
                couleur TEXT DEFAULT '#1F4E79',
                ordre INTEGER DEFAULT 0
            )
        ''')

        # Table des parametres
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS parametres (
                cle TEXT PRIMARY KEY,
                valeur TEXT,
                description TEXT
            )
        ''')

        # Table historique des prix
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historique_prix (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produit_id INTEGER,
                ancien_prix REAL,
                nouveau_prix REAL,
                date_modification TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (produit_id) REFERENCES produits(id)
            )
        ''')

        # ==================== TABLES MODULE MARCHES PUBLICS ====================

        # Table des chantiers (marches publics)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chantiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                nom_client TEXT,
                type_marche TEXT DEFAULT 'PUBLIC',
                lieu TEXT,
                type_projet TEXT,
                lot TEXT,
                montant_ht REAL DEFAULT 0,
                marge_projet REAL,
                resultat TEXT DEFAULT 'EN_COURS',
                concurrent TEXT,
                montant_concurrent REAL,
                notes TEXT,
                date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
                date_modification TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table des articles DPGF (prix_marche)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS prix_marche (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chantier_id INTEGER NOT NULL,
                code TEXT,
                niveau INTEGER DEFAULT 4,
                designation TEXT NOT NULL,
                description TEXT,
                presentation TEXT,
                categorie TEXT,
                largeur_mm INTEGER,
                hauteur_mm INTEGER,
                caracteristiques TEXT,
                unite TEXT DEFAULT 'U',
                quantite REAL DEFAULT 1,
                localisation TEXT,
                notes TEXT,
                temps_conception REAL DEFAULT 0,
                temps_fabrication REAL DEFAULT 0,
                temps_pose REAL DEFAULT 0,
                cout_materiaux REAL DEFAULT 0,
                cout_mo_total REAL DEFAULT 0,
                cout_revient REAL DEFAULT 0,
                marge_pct REAL DEFAULT 20,
                taux_tva REAL DEFAULT 20,
                prix_unitaire_ht REAL DEFAULT 0,
                prix_total_ht REAL DEFAULT 0,
                date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chantier_id) REFERENCES chantiers(id)
            )
        ''')

        # Table de liaison article DPGF <-> produits (multi-produits)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS article_produits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prix_marche_id INTEGER NOT NULL,
                produit_id INTEGER NOT NULL,
                quantite REAL DEFAULT 1,
                prix_unitaire REAL DEFAULT 0,
                FOREIGN KEY (prix_marche_id) REFERENCES prix_marche(id),
                FOREIGN KEY (produit_id) REFERENCES produits(id)
            )
        ''')

        # Table de structure hierarchique DPGF
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dpgf_structure (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chantier_id INTEGER NOT NULL,
                code TEXT,
                niveau INTEGER NOT NULL,
                designation TEXT NOT NULL,
                parent_id INTEGER,
                ordre INTEGER DEFAULT 0,
                FOREIGN KEY (chantier_id) REFERENCES chantiers(id),
                FOREIGN KEY (parent_id) REFERENCES dpgf_structure(id)
            )
        ''')

        # Index pour optimiser les recherches (milliers de produits/chantiers)
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_produits_categorie ON produits(categorie)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_produits_sous_categorie ON produits(sous_categorie)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_produits_designation ON produits(designation)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chantiers_resultat ON chantiers(resultat)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chantiers_type_marche ON chantiers(type_marche)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_prix_marche_chantier ON prix_marche(chantier_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_produits_prix_marche ON article_produits(prix_marche_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_produits_produit ON article_produits(produit_id)')

        # Parametres par defaut
        default_data_dir = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data")
        ))

        default_params = [
            ('marge', '20', 'Marge par defaut en pourcentage'),
            ('devise', 'EUR', 'Devise utilisee'),
            ('tva', '20', 'Taux de TVA en pourcentage'),
            ('entreprise', 'DestriChiffrage', 'Nom de l\'entreprise'),
            ('data_dir', default_data_dir, 'Dossier des donnees (PDF, devis, etc.)'),
            # Taux horaires pour le module marches publics - Cout entreprise
            ('taux_cout_conception', '35', 'Cout horaire conception (EUR/h)'),
            ('taux_cout_fabrication', '28', 'Cout horaire fabrication (EUR/h)'),
            ('taux_cout_pose', '32', 'Cout horaire pose (EUR/h)'),
            # Taux horaires pour le module marches publics - Prix de vente
            ('taux_vente_conception', '45', 'Prix vente horaire conception (EUR/h)'),
            ('taux_vente_fabrication', '38', 'Prix vente horaire fabrication (EUR/h)'),
            ('taux_vente_pose', '42', 'Prix vente horaire pose (EUR/h)'),
            # Marge marche (affichee mais non modifiable - calculee automatiquement)
            ('marge_marche', '25', 'Marge par defaut pour les marches publics (%)'),
        ]

        for cle, valeur, desc in default_params:
            cursor.execute('''
                INSERT OR IGNORE INTO parametres (cle, valeur, description)
                VALUES (?, ?, ?)
            ''', (cle, valeur, desc))

        # Categories par defaut (seulement si la table est vide)
        cursor.execute("SELECT COUNT(*) as cnt FROM categories")
        if cursor.fetchone()['cnt'] == 0:
            default_categories = [
                ('COUPE-FEU', 'Portes coupe-feu et techniques', '#E74C3C', 1),
                ('ACOUSTIQUE', 'Portes acoustiques', '#3498DB', 2),
                ('VITREE', 'Portes vitrees', '#2ECC71', 3),
                ('STANDARD', 'Portes standard et pleines', '#9B59B6', 4),
                ('MATERNELLE', 'Portes maternelle et creche', '#F39C12', 5),
                ('ACCESSOIRE', 'Huisseries et accessoires', '#1ABC9C', 6),
            ]

            for nom, desc, couleur, ordre in default_categories:
                cursor.execute('''
                    INSERT INTO categories (nom, description, couleur, ordre)
                    VALUES (?, ?, ?, ?)
                ''', (nom, desc, couleur, ordre))

        self.conn.commit()

        # Migration: ajouter marge_projet si elle n'existe pas
        self._migrate_chantiers_marge_projet()

    def _migrate_chantiers_marge_projet(self):
        """Ajoute la colonne marge_projet aux chantiers existants"""
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT marge_projet FROM chantiers LIMIT 1")
        except sqlite3.OperationalError:
            # La colonne n'existe pas, on l'ajoute
            cursor.execute("ALTER TABLE chantiers ADD COLUMN marge_projet REAL")
            self.conn.commit()

    # ==================== PARAMETRES ====================

    def get_parametre(self, cle: str, default: str = None) -> Optional[str]:
        """Recupere un parametre"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT valeur FROM parametres WHERE cle=?", (cle,))
        result = cursor.fetchone()
        return result['valeur'] if result else default

    def set_parametre(self, cle: str, valeur: str, description: str = None):
        """Definit un parametre"""
        cursor = self.conn.cursor()
        if description:
            cursor.execute('''
                INSERT OR REPLACE INTO parametres (cle, valeur, description)
                VALUES (?, ?, ?)
            ''', (cle, valeur, description))
        else:
            cursor.execute("UPDATE parametres SET valeur=? WHERE cle=?", (valeur, cle))
        self.conn.commit()

    def get_marge(self) -> float:
        """Recupere la marge par defaut"""
        return float(self.get_parametre('marge', '20'))

    def set_marge(self, marge: float):
        """Definit la marge par defaut"""
        self.set_parametre('marge', str(marge))

    # ==================== CATEGORIES ====================

    def get_categories(self) -> List[Dict]:
        """Recupere toutes les categories"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM categories ORDER BY ordre, nom")
        return [dict(row) for row in cursor.fetchall()]

    def get_categories_names(self) -> List[str]:
        """Recupere les noms des categories"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT nom FROM categories ORDER BY ordre, nom")
        return [row['nom'] for row in cursor.fetchall()]

    def get_subcategories_names(self, level: int = 1) -> List[str]:
        """
        Recupere les noms des sous-categories distinctes pour un niveau donne

        Args:
            level: Niveau de sous-categorie (1, 2 ou 3)

        Returns:
            Liste des sous-categories distinctes triees
        """
        cursor = self.conn.cursor()
        if level == 1:
            field = 'sous_categorie'
        elif level == 2:
            field = 'sous_categorie_2'
        elif level == 3:
            field = 'sous_categorie_3'
        else:
            return []

        cursor.execute(f"SELECT DISTINCT {field} FROM produits WHERE {field} IS NOT NULL AND {field} != '' ORDER BY {field}")
        return [row[field] for row in cursor.fetchall()]

    def get_subcategories_filtered(self, level: int = 1, categorie: str = None,
                                   sous_categorie: str = None, sous_categorie_2: str = None) -> List[str]:
        """
        Recupere les sous-categories avec filtrage en cascade

        Args:
            level: Niveau de sous-categorie a recuperer (1, 2 ou 3)
            categorie: Filtrer par categorie principale
            sous_categorie: Filtrer par sous-categorie niveau 1 (pour level >= 2)
            sous_categorie_2: Filtrer par sous-categorie niveau 2 (pour level == 3)

        Returns:
            Liste des sous-categories distinctes triees
        """
        cursor = self.conn.cursor()

        if level == 1:
            field = 'sous_categorie'
        elif level == 2:
            field = 'sous_categorie_2'
        elif level == 3:
            field = 'sous_categorie_3'
        else:
            return []

        query = f"SELECT DISTINCT {field} FROM produits WHERE {field} IS NOT NULL AND {field} != '' AND actif = 1"
        params = []

        if categorie and categorie not in ("Toutes", ""):
            query += " AND categorie = ?"
            params.append(categorie)

        if level >= 2 and sous_categorie and sous_categorie not in ("Toutes", ""):
            query += " AND sous_categorie = ?"
            params.append(sous_categorie)

        if level == 3 and sous_categorie_2 and sous_categorie_2 not in ("Toutes", ""):
            query += " AND sous_categorie_2 = ?"
            params.append(sous_categorie_2)

        query += f" ORDER BY {field}"
        cursor.execute(query, params)
        return [row[field] for row in cursor.fetchall()]

    def add_categorie(self, nom: str, description: str = None, couleur: str = '#1F4E79'):
        """Ajoute une categorie"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO categories (nom, description, couleur)
            VALUES (?, ?, ?)
        ''', (nom, description, couleur))
        self.conn.commit()

    def update_categorie(self, old_nom: str, new_nom: str, description: str = None):
        """
        Met a jour une categorie

        Args:
            old_nom: Ancien nom de la categorie
            new_nom: Nouveau nom de la categorie
            description: Nouvelle description (optionnel)
        """
        cursor = self.conn.cursor()

        if description is not None:
            cursor.execute('''
                UPDATE categories SET nom=?, description=? WHERE nom=?
            ''', (new_nom, description, old_nom))
        else:
            cursor.execute('''
                UPDATE categories SET nom=? WHERE nom=?
            ''', (new_nom, old_nom))

        # Mettre a jour les produits qui utilisent cette categorie
        if old_nom != new_nom:
            cursor.execute('''
                UPDATE produits SET categorie=?, date_modification=CURRENT_TIMESTAMP
                WHERE categorie=?
            ''', (new_nom, old_nom))

        self.conn.commit()

    def delete_categorie(self, nom: str):
        """
        Supprime une categorie

        Args:
            nom: Nom de la categorie a supprimer
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM categories WHERE nom=?", (nom,))
        self.conn.commit()

    def update_produits_category(self, old_category: str, new_category: str):
        """
        Reassigne tous les produits d'une categorie vers une autre

        Args:
            old_category: Categorie source
            new_category: Categorie destination
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE produits SET categorie=?, date_modification=CURRENT_TIMESTAMP
            WHERE categorie=?
        ''', (new_category, old_category))
        self.conn.commit()

    def delete_produits_by_category(self, category: str, permanent: bool = True):
        """
        Supprime tous les produits d'une categorie

        Args:
            category: Nom de la categorie
            permanent: Si True, supprime definitivement. Sinon, desactive.
        """
        cursor = self.conn.cursor()
        if permanent:
            cursor.execute("DELETE FROM produits WHERE categorie=?", (category,))
        else:
            cursor.execute('''
                UPDATE produits SET actif=0, date_modification=CURRENT_TIMESTAMP
                WHERE categorie=?
            ''', (category,))
        self.conn.commit()

    def get_categorie(self, nom: str) -> Optional[Dict]:
        """Recupere une categorie par son nom"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM categories WHERE nom=?", (nom,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # ==================== PRODUITS ====================

    def search_produits(self, terme: str = "", categorie: str = "", actif_only: bool = True,
                        hauteur: int = None, largeur: int = None,
                        sous_categorie: str = "", sous_categorie_2: str = "",
                        sous_categorie_3: str = "") -> List[Dict]:
        """
        Recherche des produits

        Args:
            terme: Terme de recherche (dans designation, dimensions, reference)
            categorie: Filtrer par categorie
            actif_only: Ne retourner que les produits actifs
            hauteur: Filtrer par hauteur exacte
            largeur: Filtrer par largeur exacte
            sous_categorie: Filtrer par sous-categorie 1
            sous_categorie_2: Filtrer par sous-categorie 2
            sous_categorie_3: Filtrer par sous-categorie 3

        Returns:
            Liste des produits correspondants
        """
        cursor = self.conn.cursor()
        query = "SELECT * FROM produits WHERE 1=1"
        params = []

        if actif_only:
            query += " AND actif = 1"

        if terme:
            query += " AND (designation LIKE ? OR dimensions LIKE ? OR reference LIKE ? OR sous_categorie LIKE ?)"
            terme_like = f"%{terme}%"
            params.extend([terme_like, terme_like, terme_like, terme_like])

        if categorie and categorie not in ("Toutes", ""):
            query += " AND categorie = ?"
            params.append(categorie)

        if sous_categorie and sous_categorie not in ("Toutes", ""):
            query += " AND sous_categorie = ?"
            params.append(sous_categorie)

        if sous_categorie_2 and sous_categorie_2 not in ("Toutes", ""):
            query += " AND sous_categorie_2 = ?"
            params.append(sous_categorie_2)

        if sous_categorie_3 and sous_categorie_3 not in ("Toutes", ""):
            query += " AND sous_categorie_3 = ?"
            params.append(sous_categorie_3)

        if hauteur:
            query += " AND hauteur = ?"
            params.append(hauteur)

        if largeur:
            query += " AND largeur = ?"
            params.append(largeur)

        query += " ORDER BY categorie, sous_categorie, designation"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_sous_categories(self, categorie: str = None) -> List[str]:
        """Recupere les sous-categories distinctes"""
        cursor = self.conn.cursor()
        if categorie and categorie not in ("Toutes", ""):
            cursor.execute("""SELECT DISTINCT sous_categorie FROM produits
                             WHERE actif=1 AND sous_categorie IS NOT NULL AND sous_categorie != ''
                             AND categorie=? ORDER BY sous_categorie""", (categorie,))
        else:
            cursor.execute("""SELECT DISTINCT sous_categorie FROM produits
                             WHERE actif=1 AND sous_categorie IS NOT NULL AND sous_categorie != ''
                             ORDER BY sous_categorie""")
        return [row['sous_categorie'] for row in cursor.fetchall()]

    def get_sous_categories_2(self, categorie: str = None, sous_categorie: str = None) -> List[str]:
        """Recupere les sous-categories 2 distinctes"""
        cursor = self.conn.cursor()
        query = """SELECT DISTINCT sous_categorie_2 FROM produits
                   WHERE actif=1 AND sous_categorie_2 IS NOT NULL AND sous_categorie_2 != ''"""
        params = []
        if categorie and categorie not in ("Toutes", ""):
            query += " AND categorie=?"
            params.append(categorie)
        if sous_categorie and sous_categorie not in ("Toutes", ""):
            query += " AND sous_categorie=?"
            params.append(sous_categorie)
        query += " ORDER BY sous_categorie_2"
        cursor.execute(query, params)
        return [row['sous_categorie_2'] for row in cursor.fetchall()]

    def get_sous_categories_3(self, categorie: str = None, sous_categorie: str = None,
                              sous_categorie_2: str = None) -> List[str]:
        """Recupere les sous-categories 3 distinctes"""
        cursor = self.conn.cursor()
        query = """SELECT DISTINCT sous_categorie_3 FROM produits
                   WHERE actif=1 AND sous_categorie_3 IS NOT NULL AND sous_categorie_3 != ''"""
        params = []
        if categorie and categorie not in ("Toutes", ""):
            query += " AND categorie=?"
            params.append(categorie)
        if sous_categorie and sous_categorie not in ("Toutes", ""):
            query += " AND sous_categorie=?"
            params.append(sous_categorie)
        if sous_categorie_2 and sous_categorie_2 not in ("Toutes", ""):
            query += " AND sous_categorie_2=?"
            params.append(sous_categorie_2)
        query += " ORDER BY sous_categorie_3"
        cursor.execute(query, params)
        return [row['sous_categorie_3'] for row in cursor.fetchall()]

    def get_hauteurs_distinctes(self, categorie: str = None) -> List[int]:
        """Recupere les hauteurs distinctes"""
        cursor = self.conn.cursor()
        if categorie and categorie not in ("Toutes", ""):
            cursor.execute("SELECT DISTINCT hauteur FROM produits WHERE actif=1 AND hauteur IS NOT NULL AND categorie=? ORDER BY hauteur", (categorie,))
        else:
            cursor.execute("SELECT DISTINCT hauteur FROM produits WHERE actif=1 AND hauteur IS NOT NULL ORDER BY hauteur")
        return [row['hauteur'] for row in cursor.fetchall()]

    def get_largeurs_distinctes(self, categorie: str = None, hauteur: int = None) -> List[int]:
        """Recupere les largeurs distinctes"""
        cursor = self.conn.cursor()
        query = "SELECT DISTINCT largeur FROM produits WHERE actif=1 AND largeur IS NOT NULL"
        params = []

        if categorie and categorie not in ("Toutes", ""):
            query += " AND categorie=?"
            params.append(categorie)

        if hauteur:
            query += " AND hauteur=?"
            params.append(hauteur)

        query += " ORDER BY largeur"
        cursor.execute(query, params)
        return [row['largeur'] for row in cursor.fetchall()]

    def get_fournisseurs_distincts(self) -> List[str]:
        """Recupere les fournisseurs distincts"""
        cursor = self.conn.cursor()
        query = """SELECT DISTINCT fournisseur FROM produits
                   WHERE actif=1 AND fournisseur IS NOT NULL AND fournisseur != ''
                   ORDER BY fournisseur"""
        cursor.execute(query)
        return [row['fournisseur'] for row in cursor.fetchall()]

    def get_produit(self, id: int) -> Optional[Dict]:
        """Recupere un produit par son ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM produits WHERE id=?", (id,))
        row = cursor.fetchone()
        if row:
            produit = dict(row)
            # Resoudre les chemins des fichiers
            produit['fiche_technique'] = self.resolve_fiche_path(produit.get('fiche_technique'))
            produit['devis_fournisseur'] = self.resolve_fiche_path(produit.get('devis_fournisseur'))
            return produit
        return None

    def resolve_fiche_path(self, path: str) -> str:
        """Resout le chemin d'une fiche technique (relatif -> absolu)"""
        if not path:
            return ''
        # Si c'est deja un chemin absolu, le retourner tel quel
        if os.path.isabs(path):
            return path
        # Sinon, le resoudre par rapport au dossier data
        return os.path.normpath(os.path.join(self.data_dir, path))

    def make_fiche_path_relative(self, path: str) -> str:
        """Convertit un chemin absolu en chemin relatif au dossier data"""
        if not path:
            return ''
        # Normaliser les chemins pour comparaison
        abs_data_dir = os.path.normpath(os.path.abspath(self.data_dir))
        abs_path = os.path.normpath(os.path.abspath(path))
        # Si le chemin est dans le dossier data, le rendre relatif
        if abs_path.startswith(abs_data_dir):
            return os.path.relpath(abs_path, abs_data_dir)
        # Sinon garder le chemin tel quel
        return path

    def add_produit(self, data: Dict) -> int:
        """
        Ajoute un produit

        Args:
            data: Dictionnaire avec les donnees du produit

        Returns:
            ID du produit cree
        """
        cursor = self.conn.cursor()
        # Convertir les chemins en chemins relatifs
        fiche_tech = self.make_fiche_path_relative(data.get('fiche_technique', ''))
        devis_fournisseur = self.make_fiche_path_relative(data.get('devis_fournisseur', ''))
        cursor.execute('''
            INSERT INTO produits (categorie, sous_categorie, sous_categorie_2, sous_categorie_3, designation, description, dimensions,
                                 hauteur, largeur, prix_achat, reference, fournisseur, chantier, notes,
                                 fiche_technique, devis_fournisseur)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('categorie', ''),
            data.get('sous_categorie', ''),
            data.get('sous_categorie_2', ''),
            data.get('sous_categorie_3', ''),
            data.get('designation', ''),
            data.get('description', ''),
            data.get('dimensions', ''),
            data.get('hauteur'),
            data.get('largeur'),
            data.get('prix_achat', 0),
            data.get('reference', ''),
            data.get('fournisseur', ''),
            data.get('chantier', ''),
            data.get('notes', ''),
            fiche_tech,
            devis_fournisseur
        ))
        self.conn.commit()

        # Ajouter la categorie si elle n'existe pas
        if data.get('categorie'):
            self.add_categorie(data['categorie'])

        return cursor.lastrowid

    def update_produit(self, id: int, data: Dict):
        """Met a jour un produit"""
        cursor = self.conn.cursor()

        # Sauvegarder l'historique si le prix change
        ancien = self.get_produit(id)
        if ancien and ancien['prix_achat'] != data.get('prix_achat', 0):
            cursor.execute('''
                INSERT INTO historique_prix (produit_id, ancien_prix, nouveau_prix)
                VALUES (?, ?, ?)
            ''', (id, ancien['prix_achat'], data.get('prix_achat', 0)))

        # Convertir les chemins en chemins relatifs
        fiche_tech = self.make_fiche_path_relative(data.get('fiche_technique', ''))
        devis_fournisseur = self.make_fiche_path_relative(data.get('devis_fournisseur', ''))
        cursor.execute('''
            UPDATE produits SET
                categorie=?, sous_categorie=?, sous_categorie_2=?, sous_categorie_3=?, designation=?, description=?, dimensions=?,
                hauteur=?, largeur=?, prix_achat=?, reference=?, fournisseur=?, chantier=?, notes=?,
                fiche_technique=?, devis_fournisseur=?, date_modification=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (
            data.get('categorie', ''),
            data.get('sous_categorie', ''),
            data.get('sous_categorie_2', ''),
            data.get('sous_categorie_3', ''),
            data.get('designation', ''),
            data.get('description', ''),
            data.get('dimensions', ''),
            data.get('hauteur'),
            data.get('largeur'),
            data.get('prix_achat', 0),
            data.get('reference', ''),
            data.get('fournisseur', ''),
            data.get('chantier', ''),
            data.get('notes', ''),
            fiche_tech,
            devis_fournisseur,
            id
        ))
        self.conn.commit()

    def delete_produit(self, id: int, permanent: bool = False):
        """
        Supprime un produit

        Args:
            id: ID du produit
            permanent: Si True, supprime definitivement. Sinon, desactive.
        """
        cursor = self.conn.cursor()
        if permanent:
            cursor.execute("DELETE FROM produits WHERE id=?", (id,))
        else:
            cursor.execute("UPDATE produits SET actif=0, date_modification=CURRENT_TIMESTAMP WHERE id=?", (id,))
        self.conn.commit()

    def count_produits(self, categorie: str = None) -> int:
        """Compte les produits"""
        cursor = self.conn.cursor()
        if categorie:
            cursor.execute("SELECT COUNT(*) as cnt FROM produits WHERE actif=1 AND categorie=?", (categorie,))
        else:
            cursor.execute("SELECT COUNT(*) as cnt FROM produits WHERE actif=1")
        return cursor.fetchone()['cnt']

    def clear_all_produits(self, clear_categories: bool = False):
        """
        Supprime TOUS les produits de la base de donnees
        DEPRECATED: Utiliser clear_all_data() a la place

        Args:
            clear_categories: Si True, supprime aussi toutes les categories
        """
        self.clear_all_data(clear_categories=clear_categories, clear_chantiers=False)

    def clear_all_data(self, clear_categories: bool = False, clear_chantiers: bool = True):
        """
        Supprime TOUTES les donnees de la base (produits, chantiers, etc.)
        Ne touche PAS a la table parametres

        Args:
            clear_categories: Si True, supprime aussi toutes les categories
            clear_chantiers: Si True, supprime aussi tous les chantiers et donnees associees
        """
        cursor = self.conn.cursor()

        # Supprimer les produits et historique
        cursor.execute("DELETE FROM produits")
        cursor.execute("DELETE FROM historique_prix")

        # Tables a reinitialiser (IDs)
        tables_to_reset = ['produits', 'historique_prix']

        if clear_categories:
            cursor.execute("DELETE FROM categories")
            tables_to_reset.append('categories')

        if clear_chantiers:
            # Supprimer dans l'ordre correct (contraintes FK)
            cursor.execute("DELETE FROM article_produits")
            cursor.execute("DELETE FROM prix_marche")
            cursor.execute("DELETE FROM dpgf_structure")
            cursor.execute("DELETE FROM chantiers")
            tables_to_reset.extend(['article_produits', 'prix_marche', 'dpgf_structure', 'chantiers'])

        # Reinitialiser les sequences AUTOINCREMENT
        for table in tables_to_reset:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name = ?", (table,))

        self.conn.commit()

    # ==================== IMPORT / EXPORT ====================

    def create_import_template(self, filepath: str, delimiter: str = ';'):
        """
        Cree un fichier modele pour l'import CSV

        Args:
            filepath: Chemin du fichier de sortie
            delimiter: Delimiteur CSV
        """
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=delimiter)
            # En-tetes (meme format que l'export)
            headers = ['CATEGORIE', 'SOUS-CATEGORIE', 'SOUS-CATEGORIE 2', 'SOUS-CATEGORIE 3',
                      'DESIGNATION', 'DESCRIPTION', 'HAUTEUR', 'LARGEUR', 'PRIX_UNITAIRE_HT', 'ARTICLE',
                      'FOURNISSEUR', 'CHANTIER', 'FICHE_TECHNIQUE', 'FICHIER_PDF']
            writer.writerow(headers)

            # Exemple de lignes (chemins relatifs au dossier data)
            examples = [
                ['STANDARD', 'Porte interieure', '', '', 'Porte pleine 83x204', 'Porte interieure pleine en bois massif, finition laquee blanc', '2040', '830', '125.50', 'REF001', 'Dispano', 'Projet A', 'Fiches_techniques\\porte_standard.pdf', 'Devis_fournisseur\\devis_001.pdf'],
                ['COUPE-FEU', 'EI30', 'Bloc-porte', '', 'Bloc-porte CF 1/2h', 'Bloc-porte coupe-feu EI30, ame pleine, huisserie metal', '2040', '930', '350.00', 'CF30-001', 'Dispano', 'Projet B', 'Fiches_techniques\\Portes_et_chassis\\EI30\\fiche.pdf', ''],
                ['ACOUSTIQUE', 'RA 35dB', '', '', 'Porte acoustique isolee', 'Porte acoustique haute performance, affaiblissement 35dB', '2040', '830', '280.00', 'ACO-35', 'Dispano', 'Projet C', '', 'Devis_fournisseur\\devis_002.pdf'],
            ]
            for example in examples:
                writer.writerow(example)

    def import_csv(self, filepath: str, mapping: Dict = None) -> int:
        """
        Importe des produits depuis un fichier CSV

        Args:
            filepath: Chemin du fichier CSV
            mapping: Mapping des colonnes (optionnel)

        Returns:
            Nombre de produits importes
        """
        if mapping is None:
            mapping = {
                'CATEGORIE': 'categorie',
                'SOUS-CATEGORIE': 'sous_categorie',
                'SOUS-CATEGORIE 2': 'sous_categorie_2',
                'SOUS-CATEGORIE 3': 'sous_categorie_3',
                'DESIGNATION': 'designation',
                'DESCRIPTION': 'description',
                'DIMENSIONS': 'dimensions',
                'HAUTEUR': 'hauteur',
                'LARGEUR': 'largeur',
                'PRIX_UNITAIRE_HT': 'prix_achat',
                'ARTICLE': 'reference',
                'FOURNISSEUR': 'fournisseur',
                'CHANTIER': 'chantier',
                'FICHE_TECHNIQUE': 'fiche_technique',
                'FICHIER_PDF': 'devis_fournisseur'
            }

        count = 0
        # Detecter l'encodage : utf-8-sig (avec BOM), utf-8, ou cp1252
        encoding = 'utf-8-sig'  # Detecte et supprime le BOM UTF-8 automatiquement
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as test_f:
                test_f.read(2048)  # Tester la lecture
        except UnicodeDecodeError:
            # Fallback vers cp1252 si erreur
            encoding = 'cp1252'

        with open(filepath, 'r', encoding=encoding) as f:
            # Detecter le delimiteur
            sample = f.read(1024)
            f.seek(0)
            delimiter = ';' if ';' in sample else ','

            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                data = {}
                for csv_col, db_col in mapping.items():
                    if csv_col in row:
                        value = row[csv_col]
                        if db_col == 'prix_achat':
                            try:
                                value = float(value.replace(',', '.')) if value and value not in ['divers', '-', ''] else 0
                            except:
                                value = 0
                        elif db_col in ('hauteur', 'largeur'):
                            try:
                                value = int(value) if value and value.strip().isdigit() else None
                            except:
                                value = None
                        data[db_col] = value

                # Parser dimensions si hauteur/largeur non definis
                if not data.get('hauteur') and not data.get('largeur') and data.get('dimensions'):
                    h, l = self._parse_dimensions(data['dimensions'])
                    if h:
                        data['hauteur'] = h
                    if l:
                        data['largeur'] = l

                if data.get('designation'):
                    self.add_produit(data)
                    count += 1

        return count

    def _parse_dimensions(self, dim_str: str) -> tuple:
        """Parse une chaine de dimensions pour extraire hauteur et largeur"""
        import re
        if not dim_str:
            return None, None

        # Patterns courants: "2040x830", "2040 x 830", "H2040 L830", etc.
        patterns = [
            r'(\d+)\s*[xX×]\s*(\d+)',  # 2040x830, 2040 x 830
            r'[hH][\s:]*(\d+).*[lL][\s:]*(\d+)',  # H2040 L830, H:2040 L:830
            r'(\d{3,4})\D+(\d{2,4})',  # 2040/830, 2040-830
        ]

        for pattern in patterns:
            match = re.search(pattern, dim_str)
            if match:
                try:
                    h = int(match.group(1))
                    l = int(match.group(2))
                    # Verifier que les valeurs sont coherentes (hauteur > largeur generalement)
                    if h > 0 and l > 0:
                        return (h, l) if h > l else (l, h)
                except:
                    pass

        return None, None

    def export_csv(self, filepath: str, produits: List[Dict] = None, marge: float = None,
                   include_prix_vente: bool = True, delimiter: str = ';') -> int:
        """
        Exporte des produits vers un fichier CSV

        Args:
            filepath: Chemin du fichier de sortie
            produits: Liste des produits (ou tous si None)
            marge: Marge a appliquer (ou marge par defaut si None)
            include_prix_vente: Inclure le prix de vente calcule
            delimiter: Delimiteur CSV

        Returns:
            Nombre de produits exportes
        """
        if produits is None:
            produits = self.search_produits()

        if marge is None:
            marge = self.get_marge()

        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            # En-tetes compatibles avec import (memes noms que dans le mapping)
            headers = ['CATEGORIE', 'SOUS-CATEGORIE', 'SOUS-CATEGORIE 2', 'SOUS-CATEGORIE 3',
                      'DESIGNATION', 'HAUTEUR', 'LARGEUR', 'PRIX_UNITAIRE_HT', 'ARTICLE',
                      'FOURNISSEUR', 'CHANTIER', 'FICHE_TECHNIQUE', 'FICHIER_PDF']
            if include_prix_vente:
                headers.insert(8, 'PRIX_VENTE_HT')

            writer = csv.writer(f, delimiter=delimiter)
            writer.writerow(headers)

            for p in produits:
                prix_vente = p['prix_achat'] * (1 + marge / 100)
                row = [
                    p['categorie'],
                    p['sous_categorie'],
                    p.get('sous_categorie_2', ''),
                    p.get('sous_categorie_3', ''),
                    p['designation'],
                    p['hauteur'] or '',
                    p['largeur'] or '',
                    f"{p['prix_achat']:.2f}",
                    p['reference'] or '',
                ]
                if include_prix_vente:
                    row.append(f"{prix_vente:.2f}")
                row.extend([
                    p['fournisseur'] or '',
                    p['chantier'] or '',
                    p.get('fiche_technique', '') or '',
                    p.get('devis_fournisseur', '') or ''
                ])
                writer.writerow(row)

        return len(produits)

    # ==================== PANIER / EXPORT GROUPE ====================

    def get_produits_by_ids(self, product_ids: List[int]) -> List[Dict]:
        """
        Recupere des produits par leurs IDs

        Args:
            product_ids: Liste des IDs de produits

        Returns:
            Liste des produits avec toutes leurs donnees
        """
        if not product_ids:
            return []

        cursor = self.conn.cursor()
        placeholders = ','.join('?' * len(product_ids))
        query = f"SELECT * FROM produits WHERE id IN ({placeholders}) AND actif=1"
        cursor.execute(query, product_ids)

        return [dict(row) for row in cursor.fetchall()]

    def export_cart_to_csv(self, product_ids: List[int], filepath: str,
                          export_dir: str = None, include_fiches: bool = False,
                          include_devis: bool = False, marge: float = None) -> Dict:
        """
        Exporte les produits du panier avec options de copie des PDFs

        Args:
            product_ids: Liste des IDs des produits a exporter
            filepath: Chemin du fichier CSV de destination
            export_dir: Dossier de destination pour les PDFs (optionnel)
            include_fiches: Copier les fiches techniques
            include_devis: Copier les devis fournisseur
            marge: Marge a appliquer (ou marge par defaut si None)

        Returns:
            Dictionnaire avec statistiques:
            {'nb_articles': int, 'nb_fiches': int, 'nb_devis': int}
        """
        import os
        import shutil

        # Recuperer les produits
        produits = self.get_produits_by_ids(product_ids)

        if not produits:
            return {'nb_articles': 0, 'nb_fiches': 0, 'nb_devis': 0}

        # Exporter le CSV
        nb_articles = self.export_csv(filepath, produits, marge, include_prix_vente=True)

        # Copier les PDFs si demande
        nb_fiches = 0
        nb_devis = 0

        if export_dir and (include_fiches or include_devis):
            nb_fiches, nb_devis = self._copy_pdf_files(
                produits, export_dir, include_fiches, include_devis
            )

        return {
            'nb_articles': nb_articles,
            'nb_fiches': nb_fiches,
            'nb_devis': nb_devis
        }

    def _copy_pdf_files(self, produits: List[Dict], export_dir: str,
                       include_fiches: bool, include_devis: bool) -> tuple:
        """
        Copie les fichiers PDF des produits dans un dossier d'export

        Args:
            produits: Liste des produits
            export_dir: Dossier de destination
            include_fiches: Copier les fiches techniques
            include_devis: Copier les devis fournisseur

        Returns:
            Tuple (nb_fiches_copiees, nb_devis_copies)
        """
        import os
        import shutil

        fiches_copied = 0
        devis_copied = 0

        # Creer les sous-dossiers
        if include_fiches:
            fiches_dir = os.path.join(export_dir, "Fiches_techniques")
            os.makedirs(fiches_dir, exist_ok=True)

        if include_devis:
            devis_dir = os.path.join(export_dir, "Devis_fournisseur")
            os.makedirs(devis_dir, exist_ok=True)

        # Copier les fichiers
        for product in produits:
            product_id = product['id']
            designation = product['designation']

            # Nettoyer la designation pour le nom de fichier
            safe_designation = "".join(c for c in designation if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_designation = safe_designation[:50]  # Limiter la longueur

            # Copier la fiche technique
            if include_fiches and product.get('fiche_technique'):
                src_path = self.resolve_fiche_path(product['fiche_technique'])
                if src_path and os.path.exists(src_path):
                    try:
                        ext = os.path.splitext(src_path)[1]
                        dst_name = f"{product_id}_{safe_designation}_fiche{ext}"
                        dst_path = os.path.join(fiches_dir, dst_name)
                        shutil.copy2(src_path, dst_path)
                        fiches_copied += 1
                    except Exception as e:
                        print(f"Erreur copie fiche {product_id}: {e}")

            # Copier le devis fournisseur
            if include_devis and product.get('devis_fournisseur'):
                src_path = self.resolve_fiche_path(product['devis_fournisseur'])
                if src_path and os.path.exists(src_path):
                    try:
                        ext = os.path.splitext(src_path)[1]
                        dst_name = f"{product_id}_{safe_designation}_devis{ext}"
                        dst_path = os.path.join(devis_dir, dst_name)
                        shutil.copy2(src_path, dst_path)
                        devis_copied += 1
                    except Exception as e:
                        print(f"Erreur copie devis {product_id}: {e}")

        return (fiches_copied, devis_copied)

    # ==================== STATISTIQUES ====================

    def get_stats(self) -> Dict:
        """Recupere des statistiques sur la base"""
        cursor = self.conn.cursor()

        stats = {}

        # Nombre total de produits
        cursor.execute("SELECT COUNT(*) as cnt FROM produits WHERE actif=1")
        stats['total_produits'] = cursor.fetchone()['cnt']

        # Par categorie
        cursor.execute('''
            SELECT categorie, COUNT(*) as cnt
            FROM produits WHERE actif=1
            GROUP BY categorie ORDER BY cnt DESC
        ''')
        stats['par_categorie'] = {row['categorie']: row['cnt'] for row in cursor.fetchall()}

        # Prix moyen
        cursor.execute("SELECT AVG(prix_achat) as avg_prix FROM produits WHERE actif=1 AND prix_achat > 0")
        result = cursor.fetchone()
        stats['prix_moyen'] = result['avg_prix'] if result['avg_prix'] else 0

        # Prix min/max
        cursor.execute("SELECT MIN(prix_achat) as min_prix, MAX(prix_achat) as max_prix FROM produits WHERE actif=1 AND prix_achat > 0")
        result = cursor.fetchone()
        stats['prix_min'] = result['min_prix'] if result['min_prix'] else 0
        stats['prix_max'] = result['max_prix'] if result['max_prix'] else 0

        return stats

    @staticmethod
    def copy_database_to_directory(source_db_path: str, target_data_dir: str) -> str:
        """
        Copie une base de données vers un nouveau dossier data

        Args:
            source_db_path: Chemin de la base source
            target_data_dir: Dossier data de destination

        Returns:
            Chemin de la nouvelle base de données
        """
        # Créer le dossier de destination
        os.makedirs(target_data_dir, exist_ok=True)

        # Chemin de la nouvelle base
        target_db_path = os.path.join(target_data_dir, "catalogue.db")

        # Copier le fichier
        shutil.copy2(source_db_path, target_db_path)

        # Créer les sous-dossiers nécessaires
        os.makedirs(os.path.join(target_data_dir, "Devis_fournisseur"), exist_ok=True)
        os.makedirs(os.path.join(target_data_dir, "Fiches_techniques"), exist_ok=True)

        return target_db_path

    # ==================== MODULE MARCHES PUBLICS ====================

    def get_taux_horaires(self) -> Dict[str, Dict[str, float]]:
        """Recupere les taux horaires (cout entreprise et prix de vente) pour le calcul des couts MO

        Returns:
            Dict avec structure:
            {
                'conception': {'cout': 35.0, 'vente': 45.0},
                'fabrication': {'cout': 28.0, 'vente': 38.0},
                'pose': {'cout': 32.0, 'vente': 42.0},
            }
        """
        return {
            'conception': {
                'cout': float(self.get_parametre('taux_cout_conception', '35')),
                'vente': float(self.get_parametre('taux_vente_conception', '45')),
            },
            'fabrication': {
                'cout': float(self.get_parametre('taux_cout_fabrication', '28')),
                'vente': float(self.get_parametre('taux_vente_fabrication', '38')),
            },
            'pose': {
                'cout': float(self.get_parametre('taux_cout_pose', '32')),
                'vente': float(self.get_parametre('taux_vente_pose', '42')),
            },
        }

    def get_taux_horaires_simples(self) -> Dict[str, float]:
        """Recupere uniquement les taux de vente (compatibilite)"""
        taux = self.get_taux_horaires()
        return {
            'conception': taux['conception']['vente'],
            'fabrication': taux['fabrication']['vente'],
            'pose': taux['pose']['vente'],
        }

    def get_marge_marche(self) -> float:
        """Recupere la marge par defaut pour les marches"""
        return float(self.get_parametre('marge_marche', '25'))

    # ==================== CHANTIERS ====================

    def get_chantiers(self, resultat: str = None, type_marche: str = None) -> List[Dict]:
        """Recupere tous les chantiers avec filtres optionnels"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM chantiers"
        conditions = []
        params = []
        if resultat:
            conditions.append("resultat = ?")
            params.append(resultat)
        if type_marche:
            conditions.append("type_marche = ?")
            params.append(type_marche)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY date_creation DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def get_chantier(self, chantier_id: int) -> Optional[Dict]:
        """Recupere un chantier par son ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM chantiers WHERE id = ?", (chantier_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def add_chantier(self, data: Dict) -> int:
        """Ajoute un nouveau chantier"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO chantiers (nom, nom_client, type_marche, lieu, type_projet, lot, notes, resultat, montant_ht)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('nom', ''),
            data.get('nom_client', ''),
            data.get('type_marche', 'PUBLIC'),
            data.get('lieu', ''),
            data.get('type_projet', ''),
            data.get('lot', ''),
            data.get('notes', ''),
            data.get('resultat', 'EN_COURS'),
            data.get('montant_ht', 0)
        ))
        self.conn.commit()
        return cursor.lastrowid

    def update_chantier(self, chantier_id: int, data: Dict):
        """Met a jour un chantier"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE chantiers SET
                nom = ?, nom_client = ?, type_marche = ?,
                lieu = ?, type_projet = ?, lot = ?,
                montant_ht = ?, resultat = ?, concurrent = ?,
                montant_concurrent = ?, notes = ?,
                date_modification = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (
            data.get('nom', ''),
            data.get('nom_client', ''),
            data.get('type_marche', 'PUBLIC'),
            data.get('lieu', ''),
            data.get('type_projet', ''),
            data.get('lot', ''),
            data.get('montant_ht', 0),
            data.get('resultat', 'EN_COURS'),
            data.get('concurrent', ''),
            data.get('montant_concurrent'),
            data.get('notes', ''),
            chantier_id
        ))
        self.conn.commit()

    def delete_chantier(self, chantier_id: int):
        """Supprime un chantier et toutes ses donnees associees"""
        cursor = self.conn.cursor()
        # Supprimer les produits lies aux articles
        cursor.execute('''
            DELETE FROM article_produits
            WHERE prix_marche_id IN (SELECT id FROM prix_marche WHERE chantier_id = ?)
        ''', (chantier_id,))
        # Supprimer les articles
        cursor.execute("DELETE FROM prix_marche WHERE chantier_id = ?", (chantier_id,))
        # Supprimer la structure
        cursor.execute("DELETE FROM dpgf_structure WHERE chantier_id = ?", (chantier_id,))
        # Supprimer le chantier
        cursor.execute("DELETE FROM chantiers WHERE id = ?", (chantier_id,))
        self.conn.commit()

    def update_chantier_montant(self, chantier_id: int):
        """Recalcule le montant total d'un chantier"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT SUM(prix_total_ht) as total
            FROM prix_marche WHERE chantier_id = ?
        ''', (chantier_id,))
        result = cursor.fetchone()
        total = result['total'] if result and result['total'] else 0
        cursor.execute('''
            UPDATE chantiers SET montant_ht = ?, date_modification = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (total, chantier_id))
        self.conn.commit()

    def get_chantier_recap(self, chantier_id: int) -> Dict:
        """Calcule le recapitulatif complet d'un chantier

        Returns:
            Dict avec: nb_articles, total_heures_*, total_cout_*, total_prix, marge_globale
        """
        cursor = self.conn.cursor()

        # Compter les articles
        cursor.execute("SELECT COUNT(*) as cnt FROM prix_marche WHERE chantier_id = ?", (chantier_id,))
        nb_articles = cursor.fetchone()['cnt']

        # Sommes des articles
        cursor.execute('''
            SELECT
                SUM(temps_conception) as h_conception,
                SUM(temps_fabrication) as h_fabrication,
                SUM(temps_pose) as h_pose,
                SUM(cout_materiaux) as cout_materiaux,
                SUM(cout_mo_total) as cout_mo,
                SUM(cout_revient) as cout_revient,
                SUM(prix_total_ht) as prix_total
            FROM prix_marche WHERE chantier_id = ?
        ''', (chantier_id,))
        row = cursor.fetchone()

        h_conception = row['h_conception'] or 0
        h_fabrication = row['h_fabrication'] or 0
        h_pose = row['h_pose'] or 0
        cout_materiaux = row['cout_materiaux'] or 0
        cout_mo = row['cout_mo'] or 0
        cout_revient = row['cout_revient'] or 0
        prix_total = row['prix_total'] or 0

        # Calculer la marge globale
        marge_globale = ((prix_total - cout_revient) / cout_revient * 100) if cout_revient > 0 else 0

        # Recuperer la marge projet personnalisee
        chantier = self.get_chantier(chantier_id)
        marge_projet = chantier.get('marge_projet') if chantier else None

        return {
            'nb_articles': nb_articles,
            'h_conception': h_conception,
            'h_fabrication': h_fabrication,
            'h_pose': h_pose,
            'h_total': h_conception + h_fabrication + h_pose,
            'cout_materiaux': cout_materiaux,
            'cout_mo': cout_mo,
            'cout_revient': cout_revient,
            'prix_total': prix_total,
            'marge_globale': marge_globale,
            'marge_projet': marge_projet
        }

    def set_chantier_marge_projet(self, chantier_id: int, marge: float):
        """Definit la marge projet personnalisee et recalcule tous les articles"""
        cursor = self.conn.cursor()

        # Sauvegarder la marge projet
        cursor.execute('''
            UPDATE chantiers SET marge_projet = ?, date_modification = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (marge, chantier_id))
        self.conn.commit()

        # Appliquer la marge a tous les articles du chantier
        cursor.execute("SELECT id FROM prix_marche WHERE chantier_id = ?", (chantier_id,))
        for row in cursor.fetchall():
            cursor.execute("UPDATE prix_marche SET marge_pct = ? WHERE id = ?", (marge, row['id']))
        self.conn.commit()

        # Recalculer tous les articles
        cursor.execute("SELECT id FROM prix_marche WHERE chantier_id = ?", (chantier_id,))
        for row in cursor.fetchall():
            self.recalculer_article_dpgf(row['id'])

    # ==================== ARTICLES DPGF (PRIX_MARCHE) ====================

    def get_articles_dpgf(self, chantier_id: int) -> List[Dict]:
        """Recupere tous les articles d'un chantier"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM prix_marche
            WHERE chantier_id = ?
            ORDER BY code, id
        ''', (chantier_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_article_dpgf(self, article_id: int) -> Optional[Dict]:
        """Recupere un article DPGF par son ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM prix_marche WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def add_article_dpgf(self, chantier_id: int, data: Dict) -> int:
        """Ajoute un article DPGF"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO prix_marche (
                chantier_id, code, niveau, designation, description, presentation, categorie,
                largeur_mm, hauteur_mm, caracteristiques, unite,
                quantite, localisation, notes, marge_pct, taux_tva,
                temps_conception, temps_fabrication, temps_pose
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            chantier_id,
            data.get('code', ''),
            data.get('niveau', 4),
            data.get('designation', ''),
            data.get('description', ''),
            data.get('presentation', ''),
            data.get('categorie', ''),
            data.get('largeur_mm'),
            data.get('hauteur_mm'),
            data.get('caracteristiques', ''),
            data.get('unite', 'U'),
            data.get('quantite', 1),
            data.get('localisation', ''),
            data.get('notes', ''),
            data.get('marge_pct', self.get_marge_marche()),
            data.get('taux_tva', 20),
            data.get('temps_conception', 0),
            data.get('temps_fabrication', 0),
            data.get('temps_pose', 0)
        ))
        self.conn.commit()
        article_id = cursor.lastrowid
        # Recalculer les couts initiaux
        self.recalculer_article_dpgf(article_id)
        return article_id

    def update_article_dpgf(self, article_id: int, data: Dict):
        """Met a jour un article DPGF"""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE prix_marche SET
                code = ?, designation = ?, description = ?, presentation = ?, categorie = ?,
                largeur_mm = ?, hauteur_mm = ?, caracteristiques = ?,
                unite = ?, quantite = ?, localisation = ?, notes = ?,
                temps_conception = ?, temps_fabrication = ?, temps_pose = ?,
                marge_pct = ?, taux_tva = ?
            WHERE id = ?
        ''', (
            data.get('code', ''),
            data.get('designation', ''),
            data.get('description', ''),
            data.get('presentation', ''),
            data.get('categorie', ''),
            data.get('largeur_mm'),
            data.get('hauteur_mm'),
            data.get('caracteristiques', ''),
            data.get('unite', 'U'),
            data.get('quantite', 1),
            data.get('localisation', ''),
            data.get('notes', ''),
            data.get('temps_conception', 0),
            data.get('temps_fabrication', 0),
            data.get('temps_pose', 0),
            data.get('marge_pct', 25),
            data.get('taux_tva', 20),
            article_id
        ))
        self.conn.commit()
        # Recalculer les couts
        self.recalculer_article_dpgf(article_id)

    def delete_article_dpgf(self, article_id: int):
        """Supprime un article DPGF"""
        cursor = self.conn.cursor()
        # Recuperer le chantier_id avant suppression
        cursor.execute("SELECT chantier_id FROM prix_marche WHERE id = ?", (article_id,))
        row = cursor.fetchone()
        chantier_id = row['chantier_id'] if row else None
        # Supprimer les produits lies
        cursor.execute("DELETE FROM article_produits WHERE prix_marche_id = ?", (article_id,))
        # Supprimer l'article
        cursor.execute("DELETE FROM prix_marche WHERE id = ?", (article_id,))
        self.conn.commit()
        # Mettre a jour le montant du chantier
        if chantier_id:
            self.update_chantier_montant(chantier_id)

    def recalculer_article_dpgf(self, article_id: int):
        """Recalcule les couts d'un article DPGF

        Calcule separement:
        - Cout entreprise (taux_cout_*) : cout reel pour l'entreprise
        - Prix de vente (taux_vente_*) : prix facture au client
        - Marge MO : calculee automatiquement = (vente - cout) / cout * 100
        """
        article = self.get_article_dpgf(article_id)
        if not article:
            return

        taux = self.get_taux_horaires()

        # Calculer le cout des materiaux (somme des produits lies)
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT SUM(quantite * prix_unitaire) as total
            FROM article_produits WHERE prix_marche_id = ?
        ''', (article_id,))
        result = cursor.fetchone()
        cout_materiaux = result['total'] if result and result['total'] else 0

        # Calculer les COUTS MO (cout entreprise)
        cout_mo_conception = article['temps_conception'] * taux['conception']['cout']
        cout_mo_fabrication = article['temps_fabrication'] * taux['fabrication']['cout']
        cout_mo_pose = article['temps_pose'] * taux['pose']['cout']
        cout_mo_total = cout_mo_conception + cout_mo_fabrication + cout_mo_pose

        # Calculer les PRIX DE VENTE MO
        vente_mo_conception = article['temps_conception'] * taux['conception']['vente']
        vente_mo_fabrication = article['temps_fabrication'] * taux['fabrication']['vente']
        vente_mo_pose = article['temps_pose'] * taux['pose']['vente']
        vente_mo_total = vente_mo_conception + vente_mo_fabrication + vente_mo_pose

        # Calculer la marge MO automatique
        marge_mo_pct = ((vente_mo_total - cout_mo_total) / cout_mo_total * 100) if cout_mo_total > 0 else 0

        # Cout de revient = materiaux + cout MO entreprise
        cout_revient = cout_materiaux + cout_mo_total

        # Prix de vente = materiaux + prix vente MO (pas de marge supplementaire sur materiaux)
        # On applique la marge article sur les materiaux uniquement
        marge_materiaux = article['marge_pct'] / 100
        prix_materiaux_vente = cout_materiaux * (1 + marge_materiaux)
        prix_unitaire_ht = prix_materiaux_vente + vente_mo_total
        prix_total_ht = prix_unitaire_ht * article['quantite']

        # Mettre a jour l'article
        cursor.execute('''
            UPDATE prix_marche SET
                cout_materiaux = ?, cout_mo_total = ?, cout_revient = ?,
                prix_unitaire_ht = ?, prix_total_ht = ?
            WHERE id = ?
        ''', (cout_materiaux, vente_mo_total, cout_revient, prix_unitaire_ht, prix_total_ht, article_id))
        self.conn.commit()

        # Mettre a jour le montant du chantier
        self.update_chantier_montant(article['chantier_id'])

    # ==================== PRODUITS LIES (ARTICLE_PRODUITS) ====================

    def get_produits_article(self, article_id: int) -> List[Dict]:
        """Recupere les produits lies a un article DPGF"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT ap.*, p.designation as produit_designation, p.reference,
                   p.categorie, p.prix_achat as prix_catalogue
            FROM article_produits ap
            JOIN produits p ON ap.produit_id = p.id
            WHERE ap.prix_marche_id = ?
            ORDER BY ap.id
        ''', (article_id,))
        return [dict(row) for row in cursor.fetchall()]

    def add_produit_article(self, article_id: int, produit_id: int, quantite: float = 1) -> int:
        """Ajoute un produit a un article DPGF"""
        # Recuperer le prix actuel du produit
        produit = self.get_produit(produit_id)
        if not produit:
            return -1

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO article_produits (prix_marche_id, produit_id, quantite, prix_unitaire)
            VALUES (?, ?, ?, ?)
        ''', (article_id, produit_id, quantite, produit['prix_achat']))
        self.conn.commit()

        # Recalculer l'article
        self.recalculer_article_dpgf(article_id)

        return cursor.lastrowid

    def update_produit_article(self, liaison_id: int, quantite: float, prix_unitaire: float = None):
        """Met a jour la quantite/prix d'un produit lie"""
        cursor = self.conn.cursor()
        if prix_unitaire is not None:
            cursor.execute('''
                UPDATE article_produits SET quantite = ?, prix_unitaire = ?
                WHERE id = ?
            ''', (quantite, prix_unitaire, liaison_id))
        else:
            cursor.execute('''
                UPDATE article_produits SET quantite = ?
                WHERE id = ?
            ''', (quantite, liaison_id))
        self.conn.commit()

        # Recuperer l'article_id pour recalculer
        cursor.execute("SELECT prix_marche_id FROM article_produits WHERE id = ?", (liaison_id,))
        row = cursor.fetchone()
        if row:
            self.recalculer_article_dpgf(row['prix_marche_id'])

    def remove_produit_article(self, liaison_id: int):
        """Supprime un produit d'un article DPGF"""
        cursor = self.conn.cursor()
        # Recuperer l'article_id avant suppression
        cursor.execute("SELECT prix_marche_id FROM article_produits WHERE id = ?", (liaison_id,))
        row = cursor.fetchone()
        article_id = row['prix_marche_id'] if row else None

        cursor.execute("DELETE FROM article_produits WHERE id = ?", (liaison_id,))
        self.conn.commit()

        # Recalculer l'article
        if article_id:
            self.recalculer_article_dpgf(article_id)

    # ==================== STRUCTURE DPGF ====================

    def get_structure_dpgf(self, chantier_id: int) -> List[Dict]:
        """Recupere la structure hierarchique d'un DPGF"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM dpgf_structure
            WHERE chantier_id = ?
            ORDER BY ordre, niveau, code
        ''', (chantier_id,))
        return [dict(row) for row in cursor.fetchall()]

    def add_structure_dpgf(self, chantier_id: int, data: Dict) -> int:
        """Ajoute un element de structure DPGF"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO dpgf_structure (chantier_id, code, niveau, designation, parent_id, ordre)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            chantier_id,
            data.get('code', ''),
            data.get('niveau', 1),
            data.get('designation', ''),
            data.get('parent_id'),
            data.get('ordre', 0)
        ))
        self.conn.commit()
        return cursor.lastrowid

    # ==================== IMPORT/EXPORT DPGF ====================

    def import_dpgf_csv(self, chantier_id: int, filepath: str) -> int:
        """Importe un fichier DPGF CSV"""
        count = 0
        encoding = 'utf-8-sig'
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as test_f:
                test_f.read(2048)
        except UnicodeDecodeError:
            encoding = 'cp1252'

        with open(filepath, 'r', encoding=encoding) as f:
            sample = f.read(1024)
            f.seek(0)
            delimiter = ';' if ';' in sample else ','

            reader = csv.DictReader(f, delimiter=delimiter)
            for row in reader:
                niveau = int(row.get('NIVEAU', 4)) if row.get('NIVEAU', '').isdigit() else 4

                if niveau < 4:
                    # Structure hierarchique (niveau 1-3)
                    self.add_structure_dpgf(chantier_id, {
                        'code': row.get('CODE', ''),
                        'niveau': niveau,
                        'designation': row.get('DESIGNATION', ''),
                    })
                else:
                    # Article chiffrable (niveau 4)
                    try:
                        quantite = float(row.get('QUANTITE', '1').replace(',', '.')) if row.get('QUANTITE') else 1
                    except:
                        quantite = 1

                    try:
                        largeur = int(row.get('LARGEUR_MM', '')) if row.get('LARGEUR_MM', '').isdigit() else None
                    except:
                        largeur = None

                    try:
                        hauteur = int(row.get('HAUTEUR_MM', '')) if row.get('HAUTEUR_MM', '').isdigit() else None
                    except:
                        hauteur = None

                    # Taux TVA
                    try:
                        taux_tva = float(row.get('TVA', '20').replace(',', '.')) if row.get('TVA') else 20
                    except:
                        taux_tva = 20

                    self.add_article_dpgf(chantier_id, {
                        'code': row.get('CODE', ''),
                        'niveau': 4,
                        'designation': row.get('DESIGNATION', ''),
                        'description': row.get('DESCRIPTION', ''),
                        'categorie': row.get('CATEGORIE', ''),
                        'largeur_mm': largeur,
                        'hauteur_mm': hauteur,
                        'caracteristiques': row.get('CARACTERISTIQUES', ''),
                        'unite': row.get('UNITE', 'U'),
                        'quantite': quantite,
                        'localisation': row.get('LOCALISATION', ''),
                        'notes': row.get('NOTES', ''),
                        'taux_tva': taux_tva,
                    })
                    count += 1

        return count

    def export_dpgf_csv(self, chantier_id: int, filepath: str, version_client: bool = False) -> int:
        """Exporte un DPGF vers CSV"""
        articles = self.get_articles_dpgf(chantier_id)
        structure = self.get_structure_dpgf(chantier_id)
        taux = self.get_taux_horaires()

        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            if version_client:
                # Version client simplifiee
                headers = ['CODE', 'DESIGNATION', 'UNITE', 'QUANTITE', 'PRIX_UNITAIRE_HT', 'PRIX_TOTAL_HT']
            else:
                # Version interne complete
                headers = ['CODE', 'NIVEAU', 'DESIGNATION', 'CATEGORIE', 'LARGEUR_MM', 'HAUTEUR_MM',
                          'CARACTERISTIQUES', 'UNITE', 'QUANTITE', 'LOCALISATION',
                          'TEMPS_CONCEPTION', 'TEMPS_FABRICATION', 'TEMPS_POSE',
                          'COUT_MATERIAUX', 'COUT_MO', 'COUT_REVIENT', 'MARGE_PCT',
                          'PRIX_UNITAIRE_HT', 'PRIX_TOTAL_HT', 'PRODUITS_LIES']

            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)

            # Ecrire la structure (niveaux 1-3)
            for s in structure:
                if version_client:
                    writer.writerow([s['code'], s['designation'], '', '', '', ''])
                else:
                    writer.writerow([s['code'], s['niveau'], s['designation']] + [''] * 17)

            # Ecrire les articles
            for a in articles:
                produits_lies = self.get_produits_article(a['id'])
                produits_str = ' | '.join([f"{p['produit_designation']} x{p['quantite']}" for p in produits_lies])

                if version_client:
                    writer.writerow([
                        a['code'],
                        a['designation'],
                        a['unite'],
                        a['quantite'],
                        f"{a['prix_unitaire_ht']:.2f}",
                        f"{a['prix_total_ht']:.2f}"
                    ])
                else:
                    writer.writerow([
                        a['code'],
                        a['niveau'],
                        a['designation'],
                        a['categorie'] or '',
                        a['largeur_mm'] or '',
                        a['hauteur_mm'] or '',
                        a['caracteristiques'] or '',
                        a['unite'],
                        a['quantite'],
                        a['localisation'] or '',
                        a['temps_conception'],
                        a['temps_fabrication'],
                        a['temps_pose'],
                        f"{a['cout_materiaux']:.2f}",
                        f"{a['cout_mo_total']:.2f}",
                        f"{a['cout_revient']:.2f}",
                        a['marge_pct'],
                        f"{a['prix_unitaire_ht']:.2f}",
                        f"{a['prix_total_ht']:.2f}",
                        produits_str
                    ])

        return len(articles)

    def export_dpgf_files(self, chantier_id: int, export_dir: str,
                         include_fiches: bool = True, include_devis: bool = True) -> tuple:
        """
        Exporte les fichiers PDF (fiches techniques et devis) des produits lies aux articles DPGF

        Args:
            chantier_id: ID du chantier
            export_dir: Dossier de destination
            include_fiches: Copier les fiches techniques
            include_devis: Copier les devis fournisseur

        Returns:
            Tuple (nb_fiches_copiees, nb_devis_copies)
        """
        # Recuperer tous les produits lies aux articles du chantier
        articles = self.get_articles_dpgf(chantier_id)

        # Collecter tous les produits uniques lies
        produits_ids = set()
        for article in articles:
            produits_lies = self.get_produits_article(article['id'])
            for p in produits_lies:
                produits_ids.add(p['produit_id'])

        # Recuperer les informations completes des produits
        produits = []
        for produit_id in produits_ids:
            produit = self.get_produit(produit_id)
            if produit:
                produits.append(produit)

        # Utiliser la methode existante de copie
        return self._copy_pdf_files(produits, export_dir, include_fiches, include_devis)

    def export_dpgf_odoo(self, chantier_id: int, filepath: str) -> int:
        """
        Exporte un DPGF au format Odoo CSV

        Format:
        - Ligne 1: En-tetes Odoo
        - Ligne 2: Nom client + Premier article
        - Ligne 3: Description du premier article
        - Lignes suivantes: Alternance article/description

        Args:
            chantier_id: ID du chantier
            filepath: Chemin du fichier CSV

        Returns:
            Nombre d'articles exportes
        """
        chantier = self.get_chantier(chantier_id)
        if not chantier:
            return 0

        articles = self.get_articles_dpgf(chantier_id)
        nom_client = chantier.get('nom_client', '') or chantier.get('nom', '')
        reference = chantier.get('lot', '') or ''

        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=';')

            # En-tetes Odoo
            headers = [
                'Customer*',
                'Order Lines/Products*',
                'order_line/name',
                'Order Lines/Quantity',
                'Order Lines/Unit Price',
                'Order Lines/Taxes',
                'Customer Reference'
            ]
            writer.writerow(headers)

            # Ecrire les articles
            first_article = True
            for article in articles:
                # Formatter le taux de TVA pour Odoo
                taux_tva = article.get('taux_tva', 20) or 20
                if taux_tva == int(taux_tva):
                    tva_str = f"{int(taux_tva)}% Ser"
                else:
                    tva_str = f"{taux_tva}% Ser"

                # Recuperer description et presentation
                description = article.get('description', '') or ''
                presentation = article.get('presentation', '') or ''

                # Ligne article avec description directement dans order_line/name
                writer.writerow([
                    nom_client if first_article else '',
                    article.get('designation', ''),
                    description,  # Description sur la meme ligne
                    article.get('quantite', 1),
                    f"{article.get('prix_unitaire_ht', 0):.2f}",
                    tva_str,
                    reference if first_article else ''
                ])

                # Ligne presentation (seulement si renseignee)
                if presentation:
                    writer.writerow([
                        '',
                        '',
                        presentation,
                        '',
                        '',
                        '',
                        ''
                    ])

                first_article = False

        return len(articles)

    def create_dpgf_template(self, filepath: str):
        """Cree un template DPGF CSV vierge"""
        with open(filepath, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            headers = ['CODE', 'NIVEAU', 'DESIGNATION', 'DESCRIPTION', 'CATEGORIE', 'LARGEUR_MM', 'HAUTEUR_MM',
                      'CARACTERISTIQUES', 'UNITE', 'QUANTITE', 'LOCALISATION', 'NOTES', 'TVA']
            writer.writerow(headers)

            # Exemples
            examples = [
                ['1', '1', 'LOT 1 - MENUISERIES INTERIEURES', '', '', '', '', '', '', '', '', '', ''],
                ['1.1', '2', 'Blocs-portes', '', '', '', '', '', '', '', '', '', ''],
                ['1.1.1', '3', 'Blocs-portes coupe-feu', '', '', '', '', '', '', '', '', '', ''],
                ['1.1.1.1', '4', 'Bloc-porte EI30 204x83', 'Bloc-porte coupe-feu 30 minutes avec huisserie metallique', 'COUPE-FEU', '830', '2040', 'EI30 - Huisserie metal', 'U', '5', 'Couloir RDC', '', '20'],
                ['1.1.1.2', '4', 'Bloc-porte EI60 204x93', 'Bloc-porte coupe-feu 60 minutes avec huisserie metallique', 'COUPE-FEU', '930', '2040', 'EI60 - Huisserie metal', 'U', '3', 'Escalier', '', '20'],
                ['1.1.2', '3', 'Blocs-portes acoustiques', '', '', '', '', '', '', '', '', '', ''],
                ['1.1.2.1', '4', 'Bloc-porte RA 35dB', 'Bloc-porte acoustique 35dB pour bureaux', 'ACOUSTIQUE', '830', '2040', 'RA 35dB', 'U', '8', 'Bureaux', '', '20'],
            ]
            for ex in examples:
                writer.writerow(ex)

    # ==================== STATISTIQUES MARCHES ====================

    def get_stats_marches(self) -> Dict:
        """Recupere les statistiques des marches"""
        cursor = self.conn.cursor()

        stats = {}

        # Nombre total de chantiers
        cursor.execute("SELECT COUNT(*) as cnt FROM chantiers")
        stats['total_chantiers'] = cursor.fetchone()['cnt']

        # Par resultat
        cursor.execute('''
            SELECT resultat, COUNT(*) as cnt
            FROM chantiers GROUP BY resultat
        ''')
        stats['par_resultat'] = {row['resultat']: row['cnt'] for row in cursor.fetchall()}

        # Montant total gagne
        cursor.execute("SELECT SUM(montant_ht) as total FROM chantiers WHERE resultat = 'GAGNE'")
        result = cursor.fetchone()
        stats['montant_gagne'] = result['total'] if result['total'] else 0

        # Taux de reussite
        cursor.execute("SELECT COUNT(*) as cnt FROM chantiers WHERE resultat IN ('GAGNE', 'PERDU')")
        total_termine = cursor.fetchone()['cnt']
        nb_gagne = stats['par_resultat'].get('GAGNE', 0)
        stats['taux_reussite'] = (nb_gagne / total_termine * 100) if total_termine > 0 else 0

        return stats

    def close(self):
        """Ferme la connexion"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
