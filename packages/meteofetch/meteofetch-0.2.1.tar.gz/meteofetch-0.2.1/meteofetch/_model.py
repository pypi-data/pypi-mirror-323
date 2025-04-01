from tempfile import NamedTemporaryFile
from typing import Dict, List

import cfgrib
import pandas as pd
import requests
import xarray as xr


class Model:
    """Classe de base pour le téléchargement et le traitement des données de modèles"""

    def __repr__(self):
        return f"{self.__class__.__name__}()"

    @classmethod
    def _download_file(cls, url: str) -> List[xr.Dataset]:
        """Télécharge un fichier GRIB à partir d'une URL et le charge en tant que liste de xarray.Dataset.

        Args:
            url (str): L'URL du fichier GRIB à télécharger.

        Returns:
            List[xr.Dataset]: Une liste de datasets xarray contenant les données du fichier GRIB.
        """
        with requests.get(url=url) as response:
            response.raise_for_status()
            with NamedTemporaryFile(delete=False, suffix=".grib2") as tmp_file:
                tmp_file.write(response.content)
                datasets = cfgrib.open_datasets(tmp_file.name, indexpath="")
                for k in range(len(datasets)):
                    datasets[k] = cls._process_ds(datasets[k]).load()
        return datasets

    @classmethod
    def _download_paquet(cls, date, paquet, variables) -> Dict[str, xr.DataArray]:
        """Télécharge un paquet de données pour une date et un ensemble de variables spécifiques.

        Args:
            date: La date pour laquelle télécharger les données.
            paquet: Le paquet de données à télécharger.
            variables: Les variables à extraire du paquet.

        Returns:
            Dict[str, xr.DataArray]: Un dictionnaire contenant les variables demandées sous forme de xarray.DataArray.
        """
        if isinstance(variables, str):
            variables_ = (variables,)
        else:
            variables_ = variables

        datasets = {}
        for group in cls.groups_:
            url = cls.url_.format(date=date, paquet=paquet, group=group)
            datasets_group = cls._download_file(url)
            for ds in datasets_group:
                for field in ds.data_vars:
                    if (field != "unknown") and ((variables_ is None) or (field in variables_)):
                        if field not in datasets:
                            datasets[field] = []
                        datasets[field].append(ds[field])

        for field in datasets:
            datasets[field] = xr.concat(datasets[field], dim="time").squeeze()
            ds["longitude"] = xr.where(ds["longitude"] <= 180.0, ds["longitude"], ds["longitude"] - 360.0)
        return datasets

    @classmethod
    def check_paquet(cls, paquet):
        """Vérifie si le paquet spécifié est valide."""
        if paquet not in cls.paquets_:
            raise ValueError(f"paquet must be one of {cls.paquets_}")

    @classmethod
    def get_forecast(cls, date, paquet="SP1", variables=None) -> Dict[str, xr.DataArray]:
        """Récupère les prévisions pour une date et un paquet spécifiques.

        Args:
            date: La date pour laquelle récupérer les prévisions.
            paquet (str, optional): Le paquet de données à télécharger. Par défaut "SP1".
            variables (Optional[Union[str, List[str]]], optional): Les variables à extraire. Par défaut None.

        Returns:
            Dict[str, xr.DataArray]: Un dictionnaire contenant les prévisions pour les variables demandées.
        """
        cls.check_paquet(paquet)
        date = pd.to_datetime(str(date)).floor(f"{cls.freq_update}h")
        return cls._download_paquet(date=f"{date:%Y-%m-%dT%H}", paquet=paquet, variables=variables)

    @classmethod
    def get_latest_forecast(cls, paquet="SP1", variables=None) -> Dict[str, xr.DataArray]:
        """Récupère la dernière prévision disponible pour un paquet donné.

        Args:
            paquet (str, optional): Le paquet de données à télécharger. Par défaut "SP1".
            variables (Optional[Union[str, List[str]]], optional): Les variables à extraire. Par défaut None.

        Returns:
            Dict[str, xr.DataArray]: Un dictionnaire contenant les prévisions pour les variables demandées.

        Raises:
            requests.HTTPError: Si aucune prévision n'est trouvée.
        """
        cls.check_paquet(paquet)
        date = pd.Timestamp.utcnow().floor(f"{cls.freq_update}h")
        for k in range(8):
            try:
                return cls.get_forecast(
                    date=date - pd.Timedelta(hours=cls.freq_update * k),
                    paquet=paquet,
                    variables=variables,
                )
            except requests.HTTPError:
                continue
        raise requests.HTTPError("No forecast found")
