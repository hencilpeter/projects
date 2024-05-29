from automation.automation_service import AutomationService
if __name__ == '__main__':
    print("automation-main")
    service = AutomationService(config_file= "C:\\Users\\User\\Documents\\GitHub\\projects\\TestAutomationUsingAIV2\\data\\common_config.yaml")
    service.test_sql_scripts()

