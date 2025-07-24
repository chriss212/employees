"""
Employee Management System - Refactored with Design Patterns and SOLID Principles
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Protocol, Optional
from enum import Enum
import os


# =============================================================================
# ENUMS AND CONSTANTS
# =============================================================================

class EmployeeRole(Enum):
    INTERN = "intern"
    MANAGER = "manager"
    VICE_PRESIDENT = "vice_president"


class EmployeeType(Enum):
    SALARIED = "salaried"
    HOURLY = "hourly"


FIXED_VACATION_DAYS_PAYOUT = 5


# =============================================================================
# INTERFACES AND PROTOCOLS (Dependency Inversion Principle)
# =============================================================================

class PayrollCalculator(Protocol):
    """Interface for payroll calculation strategies."""
    
    def calculate_pay(self, employee: 'Employee') -> float:
        """Calculate pay for an employee."""
        ...


class VacationManager(Protocol):
    """Interface for vacation management strategies."""
    
    def take_vacation(self, employee: 'Employee', payout: bool) -> None:
        """Handle vacation taking for an employee."""
        ...


class EmployeeRepository(Protocol):
    """Interface for employee data access."""
    
    def add_employee(self, employee: 'Employee') -> None:
        """Add an employee to the repository."""
        ...
    
    def get_all_employees(self) -> List['Employee']:
        """Get all employees."""
        ...
    
    def find_by_role(self, role: EmployeeRole) -> List['Employee']:
        """Find employees by role."""
        ...


class UIRenderer(Protocol):
    """Interface for UI rendering strategies."""
    
    def clear_screen(self) -> None:
        """Clear the screen."""
        ...
    
    def display_menu(self, options: List[str]) -> None:
        """Display menu options."""
        ...
    
    def get_input(self, prompt: str) -> str:
        """Get user input."""
        ...
    
    def display_message(self, message: str) -> None:
        """Display a message."""
        ...


# =============================================================================
# DOMAIN MODELS (Single Responsibility Principle)
# =============================================================================

@dataclass
class Employee:
    """Basic representation of an employee at the company."""
    
    name: str
    role: EmployeeRole
    vacation_days: int = 25
    
    def reduce_vacation_days(self, days: int) -> None:
        """Reduce vacation days by specified amount."""
        if self.vacation_days < days:
            raise ValueError(f"Insufficient vacation days. Available: {self.vacation_days}")
        self.vacation_days -= days


@dataclass
class SalariedEmployee(Employee):
    """Employee that's paid based on a fixed monthly salary."""
    
    monthly_salary: float = 5000.0


@dataclass
class HourlyEmployee(Employee):
    """Employee that's paid based on hourly rate."""
    
    hourly_rate: float = 50.0
    hours_worked: int = 10


# =============================================================================
# STRATEGY PATTERN IMPLEMENTATIONS
# =============================================================================

class SalariedPayrollCalculator:
    """Strategy for calculating salaried employee pay."""
    
    def calculate_pay(self, employee: Employee) -> float:
        if not isinstance(employee, SalariedEmployee):
            raise ValueError("Employee must be salaried")
        return employee.monthly_salary


class HourlyPayrollCalculator:
    """Strategy for calculating hourly employee pay."""
    
    def calculate_pay(self, employee: Employee) -> float:
        if not isinstance(employee, HourlyEmployee):
            raise ValueError("Employee must be hourly")
        return employee.hourly_rate * employee.hours_worked


class StandardVacationManager:
    """Standard vacation management strategy."""
    
    def take_vacation(self, employee: Employee, payout: bool) -> None:
        if payout:
            self._handle_payout(employee)
        else:
            self._handle_time_off(employee)
    
    def _handle_payout(self, employee: Employee) -> None:
        employee.reduce_vacation_days(FIXED_VACATION_DAYS_PAYOUT)
        print(f"Paying out vacation. Holidays left: {employee.vacation_days}")
    
    def _handle_time_off(self, employee: Employee) -> None:
        employee.reduce_vacation_days(1)
        print("Have fun on your holiday. Don't forget to check your emails!")


class ConsoleUIRenderer:
    """Console-based UI rendering strategy."""
    
    def clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_menu(self, options: List[str]) -> None:
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
    
    def get_input(self, prompt: str) -> str:
        return input(prompt)
    
    def display_message(self, message: str) -> None:
        print(message)


# =============================================================================
# REPOSITORY PATTERN (Single Responsibility)
# =============================================================================

class InMemoryEmployeeRepository:
    """In-memory implementation of employee repository."""
    
    def __init__(self):
        self._employees: List[Employee] = []
    
    def add_employee(self, employee: Employee) -> None:
        self._employees.append(employee)
    
    def get_all_employees(self) -> List[Employee]:
        return self._employees.copy()
    
    def find_by_role(self, role: EmployeeRole) -> List[Employee]:
        return [emp for emp in self._employees if emp.role == role]


# =============================================================================
# ABSTRACT FACTORY PATTERN
# =============================================================================

class AbstractEmployeeFactory(ABC):
    """Abstract factory for creating employees."""
    
    @abstractmethod
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        """Create an employee with specific parameters."""
        pass
    
    @abstractmethod
    def get_payroll_calculator(self) -> PayrollCalculator:
        """Get the appropriate payroll calculator."""
        pass


class SalariedEmployeeFactory(AbstractEmployeeFactory):
    """Factory for creating salaried employees."""
    
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        salary = kwargs.get('monthly_salary', 5000.0)
        return SalariedEmployee(name=name, role=role, monthly_salary=salary)
    
    def get_payroll_calculator(self) -> PayrollCalculator:
        return SalariedPayrollCalculator()


class HourlyEmployeeFactory(AbstractEmployeeFactory):
    """Factory for creating hourly employees."""
    
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        rate = kwargs.get('hourly_rate', 50.0)
        hours = kwargs.get('hours_worked', 10)
        return HourlyEmployee(name=name, role=role, hourly_rate=rate, hours_worked=hours)
    
    def get_payroll_calculator(self) -> PayrollCalculator:
        return HourlyPayrollCalculator()


class EmployeeFactoryProvider:
    """Provider for employee factories."""
    
    @staticmethod
    def get_factory(employee_type: EmployeeType) -> AbstractEmployeeFactory:
        factories = {
            EmployeeType.SALARIED: SalariedEmployeeFactory(),
            EmployeeType.HOURLY: HourlyEmployeeFactory()
        }
        
        factory = factories.get(employee_type)
        if not factory:
            raise ValueError(f"Unknown employee type: {employee_type}")
        return factory


# =============================================================================
# COMMAND PATTERN
# =============================================================================

class Command(ABC):
    """Abstract command interface."""
    
    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        pass


class CreateEmployeeCommand(Command):
    """Command to create an employee."""
    
    def __init__(self, factory: AbstractEmployeeFactory, repository: EmployeeRepository,
                 ui: UIRenderer, name: str, role: EmployeeRole, **kwargs):
        self._factory = factory
        self._repository = repository
        self._ui = ui
        self._name = name
        self._role = role
        self._kwargs = kwargs
    
    def execute(self) -> None:
        try:
            employee = self._factory.create_employee(self._name, self._role, **self._kwargs)
            self._repository.add_employee(employee)
            self._ui.display_message("Employee created successfully.")
        except Exception as e:
            self._ui.display_message(f"Error creating employee: {e}")


class ViewEmployeesCommand(Command):
    """Command to view employees by role."""
    
    def __init__(self, repository: EmployeeRepository, ui: UIRenderer, role: EmployeeRole):
        self._repository = repository
        self._ui = ui
        self._role = role
    
    def execute(self) -> None:
        employees = self._repository.find_by_role(self._role)
        if not employees:
            self._ui.display_message(f"No {self._role.value}s found.")
            return
        
        for emp in employees:
            self._ui.display_message(f"{emp.name} ({emp.role.value}) - {emp.vacation_days} vacation days")


class GrantVacationCommand(Command):
    """Command to grant vacation to an employee."""
    
    def __init__(self, vacation_manager: VacationManager, ui: UIRenderer,
                 employee: Employee, payout: bool):
        self._vacation_manager = vacation_manager
        self._ui = ui
        self._employee = employee
        self._payout = payout
    
    def execute(self) -> None:
        try:
            self._vacation_manager.take_vacation(self._employee, self._payout)
        except Exception as e:
            self._ui.display_message(f"Error: {e}")


class PayEmployeesCommand(Command):
    """Command to pay all employees."""
    
    def __init__(self, payroll_service: 'PayrollService', ui: UIRenderer):
        self._payroll_service = payroll_service
        self._ui = ui
    
    def execute(self) -> None:
        self._payroll_service.pay_all_employees()


# =============================================================================
# SERVICES (Single Responsibility, Open/Closed)
# =============================================================================

class PayrollService:
    """Service for handling payroll operations."""
    
    def __init__(self, repository: EmployeeRepository, ui: UIRenderer):
        self._repository = repository
        self._ui = ui
        self._calculators = {
            SalariedEmployee: SalariedPayrollCalculator(),
            HourlyEmployee: HourlyPayrollCalculator()
        }
    
    def pay_all_employees(self) -> None:
        """Pay all employees using appropriate calculators."""
        employees = self._repository.get_all_employees()
        for employee in employees:
            self._pay_employee(employee)
    
    def _pay_employee(self, employee: Employee) -> None:
        """Pay a single employee."""
        calculator = self._calculators.get(type(employee))
        if calculator:
            amount = calculator.calculate_pay(employee)
            self._ui.display_message(f"Paying {employee.name}: ${amount}")
        else:
            self._ui.display_message(f"No payroll calculator for {employee.name}")


class EmployeeService:
    """Service for employee operations."""
    
    def __init__(self, repository: EmployeeRepository, vacation_manager: VacationManager):
        self._repository = repository
        self._vacation_manager = vacation_manager
    
    def create_employee(self, employee_type: EmployeeType, name: str, 
                       role: EmployeeRole, **kwargs) -> Employee:
        """Create and add a new employee."""
        factory = EmployeeFactoryProvider.get_factory(employee_type)
        employee = factory.create_employee(name, role, **kwargs)
        self._repository.add_employee(employee)
        return employee
    
    def grant_vacation(self, employee: Employee, payout: bool) -> None:
        """Grant vacation to an employee."""
        self._vacation_manager.take_vacation(employee, payout)


# =============================================================================
# MAIN APPLICATION (Dependency Injection)
# =============================================================================

class EmployeeManagementApp:
    """Main application class with dependency injection."""
    
    def __init__(self, repository: EmployeeRepository, ui: UIRenderer,
                 vacation_manager: VacationManager):
        self._repository = repository
        self._ui = ui
        self._vacation_manager = vacation_manager
        self._payroll_service = PayrollService(repository, ui)
        self._employee_service = EmployeeService(repository, vacation_manager)
    
    def run(self) -> None:
        """Run the main application loop."""
        while True:
            self._ui.clear_screen()
            self._display_main_menu()
            
            choice = self._ui.get_input("Select an option: ")
            
            if choice == "1":
                self._handle_create_employee()
            elif choice == "2":
                self._handle_view_employees()
            elif choice == "3":
                self._handle_grant_vacation()
            elif choice == "4":
                self._handle_pay_employees()
            elif choice == "5":
                self._ui.display_message("Goodbye!")
                break
            else:
                self._ui.display_message("Invalid option.")
            
            self._ui.get_input("Press Enter to continue...")
    
    def _display_main_menu(self) -> None:
        """Display the main menu."""
        self._ui.display_message("--- Employee Management Menu ---")
        options = [
            "Create employee",
            "View employees",
            "Grant vacation to an employee",
            "Pay employees",
            "Exit"
        ]
        self._ui.display_menu(options)
    
    def _handle_create_employee(self) -> None:
        """Handle employee creation."""
        try:
            name = self._ui.get_input("Employee name: ")
            role_input = self._ui.get_input("Role (intern, manager, vice_president): ").lower()
            role = EmployeeRole(role_input)
            
            emp_type_input = self._ui.get_input("Employee type (salaried/hourly): ").lower()
            emp_type = EmployeeType(emp_type_input)
            
            kwargs = self._get_employee_creation_params(emp_type)
            
            factory = EmployeeFactoryProvider.get_factory(emp_type)
            command = CreateEmployeeCommand(factory, self._repository, self._ui, 
                                          name, role, **kwargs)
            command.execute()
            
        except (ValueError, KeyError) as e:
            self._ui.display_message(f"Invalid input: {e}")
    
    def _get_employee_creation_params(self, emp_type: EmployeeType) -> dict:
        """Get parameters for employee creation based on type."""
        if emp_type == EmployeeType.SALARIED:
            salary = float(self._ui.get_input("Monthly salary: "))
            return {'monthly_salary': salary}
        elif emp_type == EmployeeType.HOURLY:
            rate = float(self._ui.get_input("Hourly rate: "))
            hours = int(self._ui.get_input("Hours worked: "))
            return {'hourly_rate': rate, 'hours_worked': hours}
        return {}
    
    def _handle_view_employees(self) -> None:
        """Handle viewing employees by role."""
        while True:
            self._ui.clear_screen()
            self._ui.display_message("--- View Employees Submenu ---")
            
            role_options = [
                ("View managers", EmployeeRole.MANAGER),
                ("View interns", EmployeeRole.INTERN),
                ("View vice presidents", EmployeeRole.VICE_PRESIDENT),
                ("Return to main menu", None)
            ]
            
            for i, (desc, _) in enumerate(role_options):
                self._ui.display_message(f"{i+1}. {desc}")
            
            choice = self._ui.get_input("Select an option: ")
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(role_options):
                    _, role = role_options[index]
                    if role is None:
                        break
                    
                    command = ViewEmployeesCommand(self._repository, self._ui, role)
                    command.execute()
                else:
                    self._ui.display_message("Invalid option.")
            except ValueError:
                self._ui.display_message("Invalid option.")
            
            self._ui.get_input("Press Enter to continue...")
    
    def _handle_grant_vacation(self) -> None:
        """Handle granting vacation to employees."""
        employees = self._repository.get_all_employees()
        if not employees:
            self._ui.display_message("No employees available.")
            return
        
        for idx, emp in enumerate(employees):
            self._ui.display_message(f"{idx}. {emp.name} ({emp.role.value}) - {emp.vacation_days} vacation days")
        
        try:
            idx = int(self._ui.get_input("Select employee index: "))
            if 0 <= idx < len(employees):
                payout = self._ui.get_input("Payout instead of time off? (y/n): ").lower() == "y"
                
                command = GrantVacationCommand(self._vacation_manager, self._ui,
                                             employees[idx], payout)
                command.execute()
            else:
                self._ui.display_message("Invalid employee index.")
        except ValueError:
            self._ui.display_message("Invalid input.")
    
    def _handle_pay_employees(self) -> None:
        """Handle paying all employees."""
        command = PayEmployeesCommand(self._payroll_service, self._ui)
        command.execute()


# =============================================================================
# DEPENDENCY INJECTION CONTAINER
# =============================================================================

def create_app() -> EmployeeManagementApp:
    """Create the application with all dependencies injected."""
    repository = InMemoryEmployeeRepository()
    ui = ConsoleUIRenderer()
    vacation_manager = StandardVacationManager()
    
    return EmployeeManagementApp(repository, ui, vacation_manager)


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point of the application."""
    app = create_app()
    app.run()


if __name__ == "__main__":
    main() 