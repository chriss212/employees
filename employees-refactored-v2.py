from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Protocol
from enum import Enum
import os

# ENUMS AND CONSTANTS

class EmployeeRole(Enum):
    INTERN = "intern"
    MANAGER = "manager"
    VICE_PRESIDENT = "vice_president"

class EmployeeType(Enum):
    SALARIED = "salaried"
    HOURLY = "hourly"
    FREELANCER = "freelancer"

FIXED_VACATION_DAYS_PAYOUT = 5

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
    vacation_days: int = 25

    def reduce_vacation_days(self, days: int) -> None:
        if self.vacation_days < days:
            raise ValueError(f"Insufficient vacation days. Available: {self.vacation_days}")
        self.vacation_days -= days

@dataclass
class SalariedEmployee(Employee):
    monthly_salary: float = 5000.0

@dataclass
class HourlyEmployee(Employee):
    hourly_rate: float = 50.0
    hours_worked: int = 10

@dataclass
class FreelancerEmployee(Employee):
    projects: Dict[str, float] = field(default_factory=dict)

    def add_project(self, name: str, amount: float) -> None:
        self.projects[name] = amount

# STRATEGY IMPLEMENTATIONS

class SalariedPayrollCalculator:
    def calculate_pay(self, employee: Employee) -> float:
        if not isinstance(employee, SalariedEmployee):
            raise ValueError("Must be salaried")
        return employee.monthly_salary

class HourlyPayrollCalculator:
    def calculate_pay(self, employee: Employee) -> float:
        if not isinstance(employee, HourlyEmployee):
            raise ValueError("Must be hourly")
        return employee.hourly_rate * employee.hours_worked

class FreelancerPayrollCalculator:
    def calculate_pay(self, employee: Employee) -> float:
        if not isinstance(employee, FreelancerEmployee):
            raise ValueError("Must be freelancer")
        return sum(employee.projects.values())

class StandardVacationManager:
    def take_vacation(self, employee: Employee, payout: bool, days: int) -> None:
        if isinstance(employee, FreelancerEmployee):
            print("Freelancers do not have vacation benefits.")
            return
        if payout:
            employee.reduce_vacation_days(FIXED_VACATION_DAYS_PAYOUT)
        else:
            employee.reduce_vacation_days(days)

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
    @abstractmethod
    def get_payroll_calculator(self) -> PayrollCalculator: ...

class SalariedEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        return SalariedEmployee(name=name, role=role, monthly_salary=kwargs.get("monthly_salary", 5000))
    def get_payroll_calculator(self) -> PayrollCalculator:
        return SalariedPayrollCalculator()

class HourlyEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        return HourlyEmployee(name=name, role=role,
                              hourly_rate=kwargs.get("hourly_rate", 50),
                              hours_worked=kwargs.get("hours_worked", 10))
    def get_payroll_calculator(self) -> PayrollCalculator:
        return HourlyPayrollCalculator()

class FreelancerEmployeeFactory(AbstractEmployeeFactory):
    def create_employee(self, name: str, role: EmployeeRole, **kwargs) -> Employee:
        return FreelancerEmployee(name=name, role=role, projects=kwargs.get("projects", {}))
    def get_payroll_calculator(self) -> PayrollCalculator:
        return FreelancerPayrollCalculator()

class EmployeeFactoryProvider:
    @staticmethod
    def get_factory(employee_type: EmployeeType) -> AbstractEmployeeFactory:
        factories = {
            EmployeeType.SALARIED: SalariedEmployeeFactory(),
            EmployeeType.HOURLY: HourlyEmployeeFactory(),
            EmployeeType.FREELANCER: FreelancerEmployeeFactory()
        }
        return factories[employee_type]

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
        self._calculators = {
            SalariedEmployee: SalariedPayrollCalculator(),
            HourlyEmployee: HourlyPayrollCalculator(),
            FreelancerEmployee: FreelancerPayrollCalculator()
        }

    def pay_all_employees(self) -> None:
        for emp in self._repository.get_all_employees():
            calc = self._calculators.get(type(emp))
            if calc:
                amount = calc.calculate_pay(emp)
                self._ui.display_message(f"Paying {emp.name}: ${amount}")
            else:
                self._ui.display_message(f"No payroll calculator for {emp.name}")

# APP PRINCIPAL

class EmployeeManagementApp:
    def __init__(self, repo: EmployeeRepository, ui: UIRenderer, vacation_manager: VacationManager):
        self.repo = repo
        self.ui = ui
        self.vacation_manager = vacation_manager
        self.payroll_service = PayrollService(repo, ui)

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
        name = self.ui.get_input("Name: ")
        role = EmployeeRole(self.ui.get_input("Role (intern/manager/vice_president): ").lower())
        emp_type = EmployeeType(self.ui.get_input("Type (salaried/hourly/freelancer): ").lower())
        kwargs = {}

        if emp_type == EmployeeType.SALARIED:
            kwargs["monthly_salary"] = float(self.ui.get_input("Monthly salary: "))
        elif emp_type == EmployeeType.HOURLY:
            kwargs["hourly_rate"] = float(self.ui.get_input("Hourly rate: "))
            kwargs["hours_worked"] = int(self.ui.get_input("Hours worked: "))
        elif emp_type == EmployeeType.FREELANCER:
            projects = {}
            while True:
                pname = self.ui.get_input("Project name (leave empty to finish): ")
                if not pname:
                    break
                amount = float(self.ui.get_input(f"Amount for '{pname}': "))
                projects[pname] = amount
            kwargs["projects"] = projects

        factory = EmployeeFactoryProvider.get_factory(emp_type)
        employee = factory.create_employee(name, role, **kwargs)
        self.repo.add_employee(employee)
        self.ui.display_message("Employee created successfully!")

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
            days = FIXED_VACATION_DAYS_PAYOUT if payout else int(self.ui.get_input("How many vacation days?: "))
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
