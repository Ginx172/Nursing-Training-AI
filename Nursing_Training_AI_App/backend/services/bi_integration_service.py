"""
Business Intelligence Integration Service
PowerBI and Tableau connectors for Enterprise analytics
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import pandas as pd

class BIIntegrationService:
    """Service for BI tool integrations"""
    
    def __init__(self):
        pass
    
    # ========================================
    # POWER BI INTEGRATION
    # ========================================
    
    async def get_powerbi_dataset(
        self,
        organization_id: str,
        dataset_type: str  # users, questions, progress, analytics
    ) -> Dict:
        """
        Get dataset in PowerBI-compatible format
        Returns data that can be consumed by PowerBI Direct Query or Import
        """
        try:
            if dataset_type == "users":
                return await self._get_users_dataset(organization_id)
            elif dataset_type == "questions":
                return await self._get_questions_dataset(organization_id)
            elif dataset_type == "progress":
                return await self._get_progress_dataset(organization_id)
            elif dataset_type == "analytics":
                return await self._get_analytics_dataset(organization_id)
            else:
                raise ValueError(f"Unknown dataset type: {dataset_type}")
        except Exception as e:
            print(f"Error getting PowerBI dataset: {e}")
            raise
    
    async def _get_users_dataset(self, organization_id: str) -> Dict:
        """Get users dataset for PowerBI"""
        # TODO: Fetch from database
        
        users_data = {
            "schema": {
                "name": "Users",
                "columns": [
                    {"name": "UserID", "type": "string"},
                    {"name": "Name", "type": "string"},
                    {"name": "Email", "type": "string"},
                    {"name": "Band", "type": "string"},
                    {"name": "Specialty", "type": "string"},
                    {"name": "Department", "type": "string"},
                    {"name": "Team", "type": "string"},
                    {"name": "JoinedDate", "type": "datetime"},
                    {"name": "LastActive", "type": "datetime"},
                    {"name": "Status", "type": "string"}
                ]
            },
            "rows": [
                # User rows here
            ]
        }
        
        return users_data
    
    async def _get_analytics_dataset(self, organization_id: str) -> Dict:
        """Get analytics dataset for PowerBI"""
        analytics_data = {
            "schema": {
                "name": "Analytics",
                "columns": [
                    {"name": "UserID", "type": "string"},
                    {"name": "Date", "type": "date"},
                    {"name": "QuestionsAnswered", "type": "int"},
                    {"name": "QuestionsCorrect", "type": "int"},
                    {"name": "Accuracy", "type": "decimal"},
                    {"name": "TimeSpentMinutes", "type": "int"},
                    {"name": "Specialty", "type": "string"},
                    {"name": "Band", "type": "string"},
                    {"name": "QuestionType", "type": "string"}
                ]
            },
            "rows": []
        }
        
        return analytics_data
    
    def generate_powerbi_pbix_template(
        self,
        organization_id: str,
        organization_name: str
    ) -> bytes:
        """Generate PowerBI template file (.pbix)"""
        # TODO: Generate actual PBIX file
        # This would include:
        # - Data source connections
        # - Pre-built reports and dashboards
        # - Relationships between tables
        # - Calculated measures
        
        return b""  # Placeholder
    
    # ========================================
    # TABLEAU INTEGRATION
    # ========================================
    
    async def get_tableau_data_extract(
        self,
        organization_id: str,
        extract_type: str
    ) -> bytes:
        """
        Generate Tableau Data Extract (.hyper or .tde)
        """
        try:
            # TODO: Generate Tableau extract using tableauhyperapi
            
            return b""  # Placeholder
        except Exception as e:
            print(f"Error generating Tableau extract: {e}")
            raise
    
    def generate_tableau_connector(self, organization_id: str) -> str:
        """Generate Tableau Web Data Connector (WDC)"""
        
        wdc_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Nursing Training AI - Tableau Connector</title>
            <script src="https://connectors.tableau.com/libs/tableauwdc-2.3.latest.js"></script>
            <script>
                (function() {{
                    var myConnector = tableau.makeConnector();
                    
                    myConnector.getSchema = function(schemaCallback) {{
                        var cols = [
                            {{id: "user_id", dataType: tableau.dataTypeEnum.string}},
                            {{id: "questions_answered", dataType: tableau.dataTypeEnum.int}},
                            {{id: "accuracy", dataType: tableau.dataTypeEnum.float}},
                            {{id: "date", dataType: tableau.dataTypeEnum.date}}
                        ];
                        
                        var tableSchema = {{
                            id: "nursing_ai_analytics",
                            alias: "Nursing AI Analytics",
                            columns: cols
                        }};
                        
                        schemaCallback([tableSchema]);
                    }};
                    
                    myConnector.getData = function(table, doneCallback) {{
                        var apiUrl = "https://api.nursingtrainingai.com/api/analytics/export?org_id={organization_id}";
                        var apiKey = tableau.password;
                        
                        fetch(apiUrl, {{
                            headers: {{'X-API-Key': apiKey}}
                        }})
                        .then(response => response.json())
                        .then(data => {{
                            table.appendRows(data.rows);
                            doneCallback();
                        }});
                    }};
                    
                    tableau.registerConnector(myConnector);
                    
                    $(document).ready(function() {{
                        $("#submitButton").click(function() {{
                            tableau.connectionName = "Nursing Training AI";
                            tableau.submit();
                        }});
                    }});
                }})();
            </script>
        </head>
        <body>
            <h1>Nursing Training AI - Tableau Connector</h1>
            <button id="submitButton">Connect</button>
        </body>
        </html>
        """
        
        return wdc_html
    
    # ========================================
    # GENERIC DATA EXPORT
    # ========================================
    
    async def export_analytics_for_bi(
        self,
        organization_id: str,
        date_from: datetime,
        date_to: datetime,
        format: str = "json"
    ) -> Any:
        """Export analytics in BI-friendly format"""
        try:
            # TODO: Fetch analytics data
            
            data = {
                "organization_id": organization_id,
                "period": {
                    "from": date_from.isoformat(),
                    "to": date_to.isoformat()
                },
                "data": []
            }
            
            if format == "json":
                return json.dumps(data, indent=2)
            elif format == "csv":
                # TODO: Convert to CSV
                df = pd.DataFrame(data["data"])
                return df.to_csv(index=False)
            elif format == "parquet":
                # TODO: Convert to Parquet (efficient for large datasets)
                df = pd.DataFrame(data["data"])
                return df.to_parquet()
            
            return data
        except Exception as e:
            print(f"Error exporting for BI: {e}")
            raise
    
    # ========================================
    # CUSTOM SQL QUERIES (Power Users)
    # ========================================
    
    async def execute_custom_query(
        self,
        organization_id: str,
        query: str,
        parameters: Optional[Dict] = None
    ) -> Dict:
        """
        Execute custom SQL query (Enterprise only, with safeguards)
        Only allows SELECT queries on organization's own data
        """
        try:
            # Security: Only allow SELECT
            if not query.strip().upper().startswith("SELECT"):
                raise ValueError("Only SELECT queries are allowed")
            
            # Security: Check for dangerous keywords
            dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE", "ALTER"]
            query_upper = query.upper()
            for keyword in dangerous_keywords:
                if keyword in query_upper:
                    raise ValueError(f"Keyword '{keyword}' not allowed in queries")
            
            # TODO: Execute query in tenant schema
            # TODO: Apply row limit (max 10,000 rows)
            
            results = {
                "query": query,
                "executed_at": datetime.now().isoformat(),
                "row_count": 0,
                "columns": [],
                "rows": []
            }
            
            return results
        except Exception as e:
            print(f"Error executing custom query: {e}")
            raise

# Singleton instance
bi_integration_service = BIIntegrationService()

