from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Protocol, Type, TypeVar
from enum import Enum
import os

# CONFIGURATION

@dataclass
class AppConfig:
    """Application configuration to avoid magic numbers."""
    FIXED_VACATION_DAYS_PAYOUT: int = 5
    DEFAULT_MONTHLY_SALARY: float = 5000.0
    DEFAULT_HOURLY_RATE: float = 50.0
    DEFAULT_HOURS_WORKED: int = 10
    DEFAULT_VACATION_DAYS: int = 25

# Global configuration instance
config = AppConfig()

# ENUMS AND CONSTANTS

class EmployeeRole(Enum):
    INTERN = "intern"
    MANAGER = "manager"
    VICE_PRESIDENT = "vice_president"

class EmployeeType(Enum):
    SALARIED = "salaried"
    HOURLY = "hourly"
    FREELANCER = "freelancer"

# INTERFACES

class PayrollCalculator(Protocol):
    def calculate_pay(self, employee: 'Employee') -> float: ...

class VacationManager(Protocol):
    def take_vacation(self, employee: 'Employee', payout: bool, days: int) -> None: ...

class EmployeeRepository(Protocol):
    def add_employee(self, employee: 'Employee') -> None: ...
    def get_all_employees(self) -> List['Employee']: ...
    def find_by_role(self, role: EmployeeRole) -> List['Employee']: ...

class UIRenderer(Protocol):
    def clear_screen(self) -> None: ...
    def display_menu(self, options: List[str]) -> None: ...
    def get_input(self, prompt: str) -> str: ...
    def display_message(self, message: str) -> None: ...

# DOMAIN MODELS

@dataclass
class Employee:
    name: str
    role: EmployeeRole
    vacation_days: int = config.DEFAULT_VACATION_DAYS

    def reduce_vacation_days(self, days: int) -> None:
        if self.vacation_days < days:
            raise ValueError(f"Insufficient vacation days. Available: {self.vacation_days}")
        self.vacation_days -= days

@dataclass
class SalariedEmployee(Employee):
    monthly_salary: float = config.DEFAULT_MONTHLY_SALARY

@dataclass
class HourlyEmployee(Employee):
    hourly_rate: float = config.DEFAULT_HOURLY_RATE
    hours_worked: int = config.DEFAULT_HOURS_WORKED

@dataclass
class FreelancerEmployee(Employee):
    projects: Dict[str, float] = field(default_factory=dict)

    def add_project(self, name: str, amount: float) -> None:
        self.projects[name] = amount

# STRATEGY IMPLEMENTATIONS

class SalariedPayrollCalculator:
    def calculate_pay(self, employee: SalariedEmployee) -> float:
        return employee.monthly_salary

class HourlyPayrollCalculator:
    def calculate_pay(self, employee: HourlyEmployee) -> float:
        return employee.hourly_rate * employee.hours_worked

class FreelancerPayrollCalculator:
    def calculate_pay(self, employee: FreelancerEmployee) -> float:
        return sum(employee.projects.values())

class StandardVacationManager:
    def take_vacation(self, employee: Employee, payout: bool, days: int) -> None:
        if isinstance(employee, FreelancerEmployee):
            print("Freelancers do not have vacation benefits.")
            return
        if payout:
            employee.reduce_vacation_days(config.FIXED_VACATION_DAYS_PAYOUT)
        else:
            employee.reduce_vacation_days(days)

# CALCULATOR REGISTRY

class PayrollCalculatorRegistry:
    """Registry pattern to map employee types to their calculators."""
    
    def __init__(self):
        self._calculators: Dict[Type[Employee], PayrollCalculator] = {}
    
    def register(self, employee_type: Type[Employee], calculator: PayrollCalculator) -> None:
        """Register a calculator for an employee type."""
        self._calculators[employee_type] = calculator
    
    def get_calculator(self, employee_type: Type[Employee]) -> PayrollCalculator:
        """Get the calculator for an employee type."""
        calculator = self._calculators.get(employee_type)
        if not calculator:
            raise ValueError(f"No calculator registered for {employee_type.__name__}")
        return calculator
    
    def calculate_pay(self, employee: Employee) -> float:
        """Calculate pay for an employee using the appropriate calculator."""
        calculator = self.get_calculator(type(employee))
        return calculator.calculate_pay(employee)

# UI

class ConsoleUIRenderer:
    def clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
    def display_menu(self, options: List[str]) -> None:
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
    def get_input(self, prompt: str) -> str:
        return input(prompt)
    def display_message(self, message: str) -> None:
        print(message)

# REPOSITORY

class InMemoryEmployeeRepository:
    def __init__(self):
        self._employees: List[Employee] = []
    def add_employee(self, employee: Employee) -> None:
        self._employees.append(employee)
    def get_all_employees(self) -> List[Employee]:
        return self._employees.copy()
    def find_by_role(self, role: EmployeeRole) -> List[Employee]:
        return [e for e in self._employees if e.role == role]

# FACTORIES

class AbstractEmployeeFactory(ABC):
    @abstractmethod
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee: ...

class SalariedEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        return SalariedEmployee(name=name, role=role, monthly_salary=kwargs.get("monthly_salary", config.DEFAULT_MONTHLY_SALARY))

class HourlyEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        return HourlyEmployee(name=name, role=role,
                              hourly_rate=kwargs.get("hourly_rate", config.DEFAULT_HOURLY_RATE),
                              hours_worked=kwargs.get("hours_worked", config.DEFAULT_HOURS_WORKED))

class FreelancerEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        return FreelancerEmployee(name=name, role=role, projects=kwargs.get("projects", {}))

class EmployeeFactoryProvider:
    @staticmethod
    def get_factory(employee_type: EmployeeType) -> AbstractEmployeeFactory:
        factories = {
            EmployeeType.SALARIED: SalariedEmployeeFactory(),
            EmployeeType.HOURLY: HourlyEmployeeFactory(),
            EmployeeType.FREELANCER: FreelancerEmployeeFactory()
        }
        return factories[employee_type]

# INPUT VALIDATORS

class EmployeeInputValidator:
    """Validates employee input data."""
    
    @staticmethod
    def validate_name(name: str) -> str:
        if not name.strip():
            raise ValueError("Name cannot be empty")
        return name.strip()
    
    @staticmethod
    def validate_role(role_str: str) -> EmployeeRole:
        try:
            return EmployeeRole(role_str.lower())
        except ValueError:
            raise ValueError(f"Invalid role. Must be one of: {[r.value for r in EmployeeRole]}")
    
    @staticmethod
    def validate_employee_type(type_str: str) -> EmployeeType:
        try:
            return EmployeeType(type_str.lower())
        except ValueError:
            raise ValueError(f"Invalid employee type. Must be one of: {[t.value for t in EmployeeType]}")
    
    @staticmethod
    def validate_salary(salary_str: str) -> float:
        try:
            salary = float(salary_str)
            if salary <= 0:
                raise ValueError("Salary must be positive")
            return salary
        except ValueError:
            raise ValueError("Invalid salary amount")
    
    @staticmethod
    def validate_hourly_rate(rate_str: str) -> float:
        try:
            rate = float(rate_str)
            if rate <= 0:
                raise ValueError("Hourly rate must be positive")
            return rate
        except ValueError:
            raise ValueError("Invalid hourly rate")
    
    @staticmethod
    def validate_hours_worked(hours_str: str) -> int:
        try:
            hours = int(hours_str)
            if hours <= 0:
                raise ValueError("Hours worked must be positive")
            return hours
        except ValueError:
            raise ValueError("Invalid hours worked")

# COMANDO PARA VACACIONES

class GrantVacationCommand:
    def __init__(self, vacation_manager: VacationManager, ui: UIRenderer,
                 employee: Employee, payout: bool, days: int):
        self._vacation_manager = vacation_manager
        self._ui = ui
        self._employee = employee
        self._payout = payout
        self._days = days

    def execute(self) -> None:
        try:
            self._vacation_manager.take_vacation(self._employee, self._payout, self._days)
        except Exception as e:
            self._ui.display_message(f"Error: {e}")

# SERVICIO DE PAGO

class PayrollService:
    def __init__(self, repository: EmployeeRepository, ui: UIRenderer):
        self._repository = repository
        self._ui = ui
        self._calculator_registry = PayrollCalculatorRegistry()
        self._setup_calculators()
    
    def _setup_calculators(self) -> None:
        """Setup the calculator registry with all employee types."""
        self._calculator_registry.register(SalariedEmployee, SalariedPayrollCalculator())
        self._calculator_registry.register(HourlyEmployee, HourlyPayrollCalculator())
        self._calculator_registry.register(FreelancerEmployee, FreelancerPayrollCalculator())

    def pay_all_employees(self) -> None:
        for emp in self._repository.get_all_employees():
            try:
                amount = self._calculator_registry.calculate_pay(emp)
                self._ui.display_message(f"Paying {emp.name}: ${amount}")
            except Exception as e:
                self._ui.display_message(f"Error paying {emp.name}: {e}")

# APP PRINCIPAL

class EmployeeManagementApp:
    def __init__(self, repo: EmployeeRepository, ui: UIRenderer, vacation_manager: VacationManager):
        self.repo = repo
        self.ui = ui
        self.vacation_manager = vacation_manager
        self.payroll_service = PayrollService(repo, ui)
        self.validator = EmployeeInputValidator()

    def run(self):
        while True:
            self.ui.clear_screen()
            self.ui.display_menu([
                "Create employee",
                "Grant vacation",
                "View employees",
                "Pay employees",
                "Exit"
            ])
            choice = self.ui.get_input("Choice: ")
            if choice == "1":
                self._create_employee()
            elif choice == "2":
                self._grant_vacation()
            elif choice == "3":
                self._view_employees()
            elif choice == "4":
                self.payroll_service.pay_all_employees()
            elif choice == "5":
                break
            else:
                self.ui.display_message("Invalid choice.")
            self.ui.get_input("Press Enter to continue...")

    def _create_employee(self):
        """Create a new employee with input validation."""
        try:
            name = self._get_employee_name()
            role = self._get_employee_role()
            emp_type = self._get_employee_type()
            kwargs = self._get_employee_specific_data(emp_type)
            
            factory = EmployeeFactoryProvider.get_factory(emp_type)
            employee = factory.create_employee(name, role, **kwargs)
            self.repo.add_employee(employee)
            self.ui.display_message("Employee created successfully!")
        except Exception as e:
            self.ui.display_message(f"Error creating employee: {e}")

    def _get_employee_name(self) -> str:
        """Get and validate employee name."""
        name = self.ui.get_input("Name: ")
        return self.validator.validate_name(name)

    def _get_employee_role(self) -> EmployeeRole:
        """Get and validate employee role."""
        role_input = self.ui.get_input("Role (intern/manager/vice_president): ")
        return self.validator.validate_role(role_input)

    def _get_employee_type(self) -> EmployeeType:
        """Get and validate employee type."""
        type_input = self.ui.get_input("Type (salaried/hourly/freelancer): ")
        return self.validator.validate_employee_type(type_input)

    def _get_employee_specific_data(self, emp_type: EmployeeType) -> Dict:
        """Get employee type-specific data with validation."""
        kwargs = {}

        if emp_type == EmployeeType.SALARIED:
            salary_input = self.ui.get_input("Monthly salary: ")
            kwargs["monthly_salary"] = self.validator.validate_salary(salary_input)
        elif emp_type == EmployeeType.HOURLY:
            rate_input = self.ui.get_input("Hourly rate: ")
            kwargs["hourly_rate"] = self.validator.validate_hourly_rate(rate_input)
            hours_input = self.ui.get_input("Hours worked: ")
            kwargs["hours_worked"] = self.validator.validate_hours_worked(hours_input)
        elif emp_type == EmployeeType.FREELANCER:
            kwargs["projects"] = self._get_freelancer_projects()

        return kwargs

    def _get_freelancer_projects(self) -> Dict[str, float]:
        """Get freelancer project data."""
        projects = {}
        self.ui.display_message("Enter project details (leave project name empty to finish):")
        
        while True:
            pname = self.ui.get_input("Project name: ").strip()
            if not pname:
                break
            try:
                amount = float(self.ui.get_input(f"Amount for '{pname}': "))
                if amount <= 0:
                    self.ui.display_message("Project amount must be positive")
                    continue
                projects[pname] = amount
            except ValueError:
                self.ui.display_message("Invalid project amount")
                continue
        
        return projects

    def _grant_vacation(self):
        employees = self.repo.get_all_employees()
        if not employees:
            self.ui.display_message("No employees available.")
            return

        for i, emp in enumerate(employees):
            self.ui.display_message(f"{i}. {emp.name} ({emp.vacation_days} days left)")

        try:
            idx = int(self.ui.get_input("Select employee index: "))
            if idx < 0 or idx >= len(employees):
                raise ValueError("Invalid index")

            emp = employees[idx]
            payout = self.ui.get_input("Payout instead of time off? (y/n): ").lower() == "y"
            days = config.FIXED_VACATION_DAYS_PAYOUT if payout else int(self.ui.get_input("How many vacation days?: "))
            cmd = GrantVacationCommand(self.vacation_manager, self.ui, emp, payout, days)
            cmd.execute()
        except Exception as e:
            self.ui.display_message(f"Error: {e}")

    def _view_employees(self):
        for emp in self.repo.get_all_employees():
            self.ui.display_message(f"{emp.name} - {emp.role.value} - {emp.vacation_days} days")
            if isinstance(emp, FreelancerEmployee):
                for pname, amt in emp.projects.items():
                    self.ui.display_message(f"  Project: {pname}, Amount: ${amt}")

# MAIN

def main():
    repo = InMemoryEmployeeRepository()
    ui = ConsoleUIRenderer()
    vacation_manager = StandardVacationManager()
    app = EmployeeManagementApp(repo, ui, vacation_manager)
    app.run()

if __name__ == "__main__":
    main()
