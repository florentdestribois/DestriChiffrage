"""
DestriChiffrage - Module Base de Donnees
=========================================
Gestion de la base de donnees SQLite pour le catalogue de portes
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
                        hauteur: int = None, largeur: int = None) -> List[Dict]:
        """
        Recherche des produits

        Args:
            terme: Terme de recherche (dans designation, dimensions, reference)
            categorie: Filtrer par categorie
            actif_only: Ne retourner que les produits actifs
            hauteur: Filtrer par hauteur exacte
            largeur: Filtrer par largeur exacte

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

        if hauteur:
            query += " AND hauteur = ?"
            params.append(hauteur)

        if largeur:
            query += " AND largeur = ?"
            params.append(largeur)

        query += " ORDER BY categorie, sous_categorie, designation"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

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

    def get_produit(self, id: int) -> Optional[Dict]:
        """Recupere un produit par son ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM produits WHERE id=?", (id,))
        row = cursor.fetchone()
        if row:
            produit = dict(row)
            # Resoudre le chemin de la fiche technique
            produit['fiche_technique'] = self.resolve_fiche_path(produit.get('fiche_technique'))
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
            INSERT INTO produits (categorie, sous_categorie, sous_categorie_2, sous_categorie_3, designation, dimensions,
                                 hauteur, largeur, prix_achat, reference, fournisseur, chantier, notes,
                                 fiche_technique, devis_fournisseur)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('categorie', ''),
            data.get('sous_categorie', ''),
            data.get('sous_categorie_2', ''),
            data.get('sous_categorie_3', ''),
            data.get('designation', ''),
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
                categorie=?, sous_categorie=?, sous_categorie_2=?, sous_categorie_3=?, designation=?, dimensions=?,
                hauteur=?, largeur=?, prix_achat=?, reference=?, fournisseur=?, chantier=?, notes=?,
                fiche_technique=?, devis_fournisseur=?, date_modification=CURRENT_TIMESTAMP
            WHERE id=?
        ''', (
            data.get('categorie', ''),
            data.get('sous_categorie', ''),
            data.get('sous_categorie_2', ''),
            data.get('sous_categorie_3', ''),
            data.get('designation', ''),
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

    def clear_all_produits(self):
        """Supprime TOUS les produits de la base de donnees"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM produits")
        cursor.execute("DELETE FROM historique_prix")
        self.conn.commit()

    # ==================== IMPORT / EXPORT ====================

    def create_import_template(self, filepath: str, delimiter: str = ';'):
        """
        Cree un fichier modele pour l'import CSV

        Args:
            filepath: Chemin du fichier de sortie
            delimiter: Delimiteur CSV
        """
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=delimiter)
            # En-tetes
            headers = ['CATEGORIE', 'SOUS-CATEGORIE', 'DESIGNATION', 'HAUTEUR', 'LARGEUR',
                      'PRIX_UNITAIRE_HT', 'ARTICLE', 'FOURNISSEUR', 'CHANTIER', 'FICHE_TECHNIQUE']
            writer.writerow(headers)

            # Exemple de lignes (chemins relatifs au dossier data)
            examples = [
                ['STANDARD', 'Porte interieure', 'Porte pleine 83x204', '2040', '830', '125.50', 'REF001', 'Dispano', 'Projet A', 'Fiches techniques\\porte_standard.pdf'],
                ['COUPE-FEU', 'EI30', 'Bloc-porte CF 1/2h', '2040', '930', '350.00', 'CF30-001', 'Dispano', 'Projet B', 'Fiches techniques\\Portes et chassis\\EI30\\fiche.pdf'],
                ['ACOUSTIQUE', 'RA 35dB', 'Porte acoustique isolee', '2040', '830', '280.00', 'ACO-35', 'Dispano', 'Projet C', ''],
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
        # Essayer d'ouvrir avec utf-8, sinon cp1252
        encoding = 'utf-8'
        try:
            with open(filepath, 'r', encoding='utf-8') as test_f:
                test_f.read(2048)  # Tester la lecture
        except UnicodeDecodeError:
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

        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            headers = ['CATEGORIE', 'SOUS_CATEGORIE', 'SOUS_CATEGORIE_2', 'SOUS_CATEGORIE_3', 'DESIGNATION', 'HAUTEUR', 'LARGEUR',
                      'PRIX_ACHAT_HT', 'REFERENCE', 'FOURNISSEUR', 'CHANTIER', 'FICHE_TECHNIQUE']
            if include_prix_vente:
                headers.insert(6, 'PRIX_VENTE_HT')

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
                ]
                if include_prix_vente:
                    row.append(f"{prix_vente:.2f}")
                row.extend([p['reference'], p['fournisseur'] or '', p['chantier'] or '', p.get('fiche_technique') or ''])
                writer.writerow(row)

        return len(produits)

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

    def close(self):
        """Ferme la connexion"""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
