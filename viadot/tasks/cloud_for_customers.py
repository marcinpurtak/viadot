from prefect import task, Task
import pandas as pd
from ..sources import CloudForCustomers
from typing import Any, Dict, List
from prefect.utilities.tasks import defaults_from_attrs


class C4CReportToDF(Task):
    def __init__(
        self,
        *args,
        report_url: str = None,
        env: str = "QA",
        skip: int = 0,
        top: int = 1000,
        **kwargs,
    ):

        self.report_url = report_url
        self.env = env
        self.skip = skip
        self.top = top

        super().__init__(
            name="c4c_report_to_df",
            *args,
            **kwargs,
        )

    def __call__(self, *args, **kwargs):
        """Download report to DF"""
        return super().__call__(*args, **kwargs)

    @defaults_from_attrs(
        "report_url",
        "env",
        "skip",
        "top",
    )
    def run(
        self,
        report_url: str = None,
        env: str = "QA",
        skip: int = 0,
        top: int = 1000,
    ):
        """
        Task run method.

        Args:
            report_url (str, optional): The url to the API in case of prepared report. Defaults to None.
            env (str, optional): The development environments. Defaults to 'QA'.
            skip (int, optional): Initial index value of reading row. Defaults to 0.
            top (int, optional): The value of top reading row. Defaults to 1000.

        Returns:
            pd.DataFrame: The query result as a pandas DataFrame.
        """
        final_df = pd.DataFrame()
        next_batch = True
        while next_batch:
            new_url = f"{report_url}&$top={top}&$skip={skip}"
            print(f"new_url: {new_url}")
            chunk_from_url = CloudForCustomers(url=new_url, env=env)
            df = chunk_from_url.to_df()
            final_df = final_df.append(df)
            if not final_df.empty:
                df_count = df.count()[1]
                if df_count != top:
                    next_batch = False
                skip += top
            else:
                break
        return final_df


class C4CToDF(Task):
    def __init__(
        self,
        *args,
        url: str = None,
        endpoint: str = None,
        fields: List[str] = None,
        params: Dict[str, Any] = {},
        env: str = "QA",
        if_empty: str = "warn",
        **kwargs,
    ):

        self.url = url
        self.endpoint = endpoint
        self.fields = fields
        self.params = params
        self.env = env
        self.if_empty = if_empty

        super().__init__(
            name="c4c_to_df",
            *args,
            **kwargs,
        )

    @defaults_from_attrs("url", "endpoint", "fields", "params", "env", "if_empty")
    def run(
        self,
        url: str = None,
        endpoint: str = None,
        fields: List[str] = None,
        params: List[str] = None,
        env: str = "QA",
        if_empty: str = "warn",
    ):
        """
        Task run method.

        Args:
            url (str, optional): The url to the API in case of prepared report. Defaults to None.
            env (str, optional): The development environments. Defaults to 'QA'.

        Returns:
            pd.DataFrame: The query result as a pandas DataFrame.
        """
        cloud_for_customers = CloudForCustomers(
            url=url, params=params, endpoint=endpoint, env=env, fields=fields
        )

        df = cloud_for_customers.to_df(if_empty=if_empty, fields=fields)

        return df
