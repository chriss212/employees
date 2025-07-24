import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Type, Callable

# Constants
FIXED_VACATION_DAYS_PAYOUT = 5

# --- SOLID Principles & Design Patterns ---

## Single Responsibility Principle (SRP)
## Open/Closed Principle (OCP)
## Liskov Substitution Principle (LSP)
## Interface Segregation Principle (ISP)
## Dependency Inversion Principle (DIP)

# 1. Employee Base and Concrete Implementations (LSP, OCP)
# 2. Strategy Pattern for Payment and Vacation Handling
# 3. Abstract Factory for Employee Creation
# 4. Command Pattern for Actions
# 5. Dependency Injection for managing dependencies


## Core Abstractions and Base Classes

### Employee Base
@dataclass
class Employee(ABC):
    """Abstract base class for all employees."""
    name: str
    role: str
    vacation_days: int = 25

    @abstractmethod
    def calculate_pay(self) -> float:
        """Abstract method to calculate employee's pay."""
        pass

    def get_info(self) -> str:
        """Returns basic employee information."""
        return f"{self.name} ({self.role}) - {self.vacation_days} vacation days remaining."


### Employee Concrete Implementations

@dataclass
class SalariedEmployee(Employee):
    """Employee paid a fixed monthly salary."""
    monthly_salary: float = 5000.0

    def calculate_pay(self) -> float:
        return self.monthly_salary

@dataclass
class HourlyEmployee(Employee):
    """Employee paid based on hours worked."""
    hourly_rate: float = 50.0
    hours_worked: int = 10

    def calculate_pay(self) -> float:
        return self.hourly_rate * self.hours_worked


## Strategy Pattern

# The Strategy pattern is used to define a family of algorithms, encapsulate each one, and make them interchangeable. This helps in adhering to the Open/Closed Principle (OCP) by allowing new payment or vacation strategies to be added without modifying existing employee classes.

### Payment Strategy
class PaymentStrategy(ABC):
    """Abstract strategy for employee payment."""
    @abstractmethod
    def pay(self, employee: Employee) -> None:
        pass

class SalariedPaymentStrategy(PaymentStrategy):
    """Payment strategy for salaried employees."""
    def pay(self, employee: SalariedEmployee) -> None:
        print(f"Paying employee {employee.name} a monthly salary of ${employee.calculate_pay():.2f}.")

class HourlyPaymentStrategy(PaymentStrategy):
    """Payment strategy for hourly employees."""
    def pay(self, employee: HourlyEmployee) -> None:
        print(f"Paying employee {employee.name} an hourly wage of ${employee.calculate_pay():.2f}.")

### Vacation Strategy
class VacationStrategy(ABC):
    """Abstract strategy for handling employee vacation."""
    @abstractmethod
    def handle_vacation(self, employee: Employee, payout: bool) -> None:
        pass

class DefaultVacationStrategy(VacationStrategy):
    """Default vacation handling strategy."""
    def handle_vacation(self, employee: Employee, payout: bool) -> None:
        if payout:
            if employee.vacation_days < FIXED_VACATION_DAYS_PAYOUT:
                raise ValueError(
                    f"You don't have enough holidays left over for a payout. "
                    f"Remaining holidays: {employee.vacation_days}."
                )
            employee.vacation_days -= FIXED_VACATION_DAYS_PAYOUT
            print(f"Paying out a holiday. Holidays left: {employee.vacation_days}")
        else:
            if employee.vacation_days < 1:
                raise ValueError(
                    "You don't have any holidays left. Now back to work, you!"
                )
            employee.vacation_days -= 1
            print("Have fun on your holiday. Don't forget to check your emails!")


## Abstract Factory Pattern

# The Abstract Factory pattern provides an interface for creating families of related or dependent objects without specifying their concrete classes. This adheres to the Dependency Inversion Principle (DIP) and helps in creating different types of employees without coupling the client code to concrete employee classes.

### Employee Factory Base
class EmployeeFactory(ABC):
    """Abstract factory for creating employees."""
    @abstractmethod
    def create_employee(self, name: str, role: str, **kwargs) -> Employee:
        pass

### Concrete Employee Factories
class SalariedEmployeeFactory(EmployeeFactory):
    """Concrete factory for creating salaried employees."""
    def create_employee(self, name: str, role: str, **kwargs) -> Employee:
        # Let the dataclass handle default values and argument validation.
        return SalariedEmployee(name=name, role=role, **kwargs)

class HourlyEmployeeFactory(EmployeeFactory):
    """Concrete factory for creating hourly employees."""
    def create_employee(self, name: str, role: str, **kwargs) -> Employee:
        # Let the dataclass handle default values and argument validation.
        return HourlyEmployee(name=name, role=role, **kwargs)

### Factory Provider
class EmployeeFactoryProvider:
    """Provides the correct employee factory based on type."""
    def __init__(self):
        self._factories: Dict[str, EmployeeFactory] = {
            "salaried": SalariedEmployeeFactory(),
            "hourly": HourlyEmployeeFactory(),
        }

    def get_factory(self, emp_type: str) -> EmployeeFactory:
        factory = self._factories.get(emp_type)
        if not factory:
            raise ValueError(f"No factory found for employee type: {emp_type}")
        return factory


## Command Pattern

# The Command pattern encapsulates a request as an object, thereby letting you parameterize clients with different requests, queue or log requests, and support undoable operations. This helps decouple the invoker (e.g., the menu options) from the receiver (the actual operation).

### Command Interface
class Command(ABC):
    """Abstract base class for all commands."""
    @abstractmethod
    def execute(self) -> None:
        pass

### Concrete Commands
class AddEmployeeCommand(Command):
    """Command to add an employee."""
    def __init__(self, company: "Company", employee: Employee):
        self._company = company
        self._employee = employee

    def execute(self) -> None:
        self._company.add_employee(self._employee)
        print("Employee created successfully.")

class TakeHolidayCommand(Command):
    """Command to allow an employee to take a holiday."""
    def __init__(self, employee: Employee, payout: bool, vacation_strategy: VacationStrategy):
        self._employee = employee
        self._payout = payout
        self._vacation_strategy = vacation_strategy

    def execute(self) -> None:
        self._vacation_strategy.handle_vacation(self._employee, self._payout)

class PayEmployeeCommand(Command):
    """Command to pay a single employee."""
    def __init__(self, employee: Employee, payment_strategy: PaymentStrategy):
        self._employee = employee
        self._payment_strategy = payment_strategy

    def execute(self) -> None:
        self._payment_strategy.pay(self._employee)

class PayAllEmployeesCommand(Command):
    """Command to pay all employees."""
    def __init__(self, company: "Company", payment_strategies: Dict[Type[Employee], PaymentStrategy]):
        self._company = company
        self._payment_strategies = payment_strategies

    def execute(self) -> None:
        for employee in self._company.employees:
            strategy = self._payment_strategies.get(type(employee))
            if strategy:
                strategy.pay(employee)
            else:
                print(f"No payment strategy found for {type(employee).__name__}.")

class ViewEmployeesCommand(Command):
    """Abstract base command for viewing employees."""
    def __init__(self, company: "Company"):
        self._company = company

    @abstractmethod
    def execute(self) -> None:
        pass

class ViewManagersCommand(ViewEmployeesCommand):
    """Command to view managers."""
    def execute(self) -> None:
        managers = self._company.find_employees_by_role("manager")
        if not managers:
            print("No managers found.")
            return
        for emp in managers:
            print(emp.get_info())

class ViewInternsCommand(ViewEmployeesCommand):
    """Command to view interns."""
    def execute(self) -> None:
        interns = self._company.find_employees_by_role("intern")
        if not interns:
            print("No interns found.")
            return
        for emp in interns:
            print(emp.get_info())

class ViewVicePresidentsCommand(ViewEmployeesCommand):
    """Command to view vice presidents."""
    def execute(self) -> None:
        vps = self._company.find_employees_by_role("vice_president")
        if not vps:
            print("No vice presidents found.")
            return
        for emp in vps:
            print(emp.get_info())

## Dependency Injection (DI)

# Dependency Injection is a technique where an object receives other objects that it depends on. This makes classes more independent and testable, reduces coupling, and improves maintainability.

### IoC Container (Simple Implementation)
class IoCContainer:
    """A simple Inversion of Control container for dependency injection."""
    def __init__(self):
        self._dependencies: Dict[Type, Callable] = {}

    def register(self, interface: Type, concrete_impl: Callable):
        self._dependencies[interface] = concrete_impl

    def resolve(self, interface: Type):
        factory = self._dependencies.get(interface)
        if not factory:
            raise ValueError(f"No dependency registered for {interface.__name__}")
        return factory()

# Global container instance
container = IoCContainer()


## Refactored Company Class

# The `Company` class is now cleaner, focusing solely on managing employees. Employee creation, payment logic, and vacation logic are delegated to their respective strategies and factories.

class Company:
    """Represents a company with employees."""
    def __init__(self, vacation_strategy: VacationStrategy):
        self.employees: List[Employee] = []
        self._vacation_strategy = vacation_strategy # Injected dependency

    def add_employee(self, employee: Employee) -> None:
        """Add an employee to the list of employees."""
        self.employees.append(employee)

    def find_employees_by_role(self, role: str) -> List[Employee]:
        """Find all employees by a specific role."""
        return [employee for employee in self.employees if employee.role == role]

    def get_employee_by_index(self, index: int) -> Employee:
        """Gets an employee by index, with bounds checking."""
        if not 0 <= index < len(self.employees):
            raise IndexError("Employee index out of bounds.")
        return self.employees[index]

    def handle_employee_vacation(self, employee: Employee, payout: bool) -> None:
        """Delegates vacation handling to the injected strategy."""
        self._vacation_strategy.handle_vacation(employee, payout)



## Helper Functions and Main Application Flow

def clear_screen():
    """Clears the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def get_employee_details_from_user(employee_factory_provider: EmployeeFactoryProvider) -> Employee | None:
    """Prompts user for employee details and creates an employee."""
    name = input("Employee name: ")
    role = input("Role (intern, manager, vice_president): ").lower()
    emp_type = input("Employee type (salaried/hourly): ").lower()

    try:
        factory = employee_factory_provider.get_factory(emp_type)
        if emp_type == "salaried":
            salary = float(input("Monthly salary: "))
            return factory.create_employee(name=name, role=role, monthly_salary=salary)
        elif emp_type == "hourly":
            rate = float(input("Hourly rate: "))
            hours = int(input("Hours worked: "))
            return factory.create_employee(name=name, role=role, hourly_rate=rate, hours_worked=hours)
        else:
            print("Invalid employee type.")
            return None
    except ValueError as e:
        print(f"Invalid input: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def main():
    # --- Dependency Registration ---
    container.register(VacationStrategy, DefaultVacationStrategy)
    container.register(EmployeeFactoryProvider, EmployeeFactoryProvider)
    container.register(SalariedPaymentStrategy, SalariedPaymentStrategy)
    container.register(HourlyPaymentStrategy, HourlyPaymentStrategy)

    # --- Dependency Resolution (Manual for this example) ---
    vacation_strategy = container.resolve(VacationStrategy)
    employee_factory_provider = container.resolve(EmployeeFactoryProvider)
    salaried_payment_strategy = container.resolve(SalariedPaymentStrategy)
    hourly_payment_strategy = container.resolve(HourlyPaymentStrategy)

    company = Company(vacation_strategy)

    # Map employee types to their payment strategies for the PayAllEmployeesCommand
    payment_strategies = {
        SalariedEmployee: salaried_payment_strategy,
        HourlyEmployee: hourly_payment_strategy,
    }

    while True:
        clear_screen()
        print("--- Employee Management Menu ---")
        print("1. Create employee")
        print("2. View employees")
        print("3. Grant vacation to an employee")
        print("4. Pay employees")
        print("5. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            employee = get_employee_details_from_user(employee_factory_provider)
            if employee:
                command = AddEmployeeCommand(company, employee)
                command.execute()
            input("Press Enter to continue...")

        elif choice == "2":
            while True:
                clear_screen()
                print("--- View Employees Submenu ---")
                print("1. View managers")
                print("2. View interns")
                print("3. View vice presidents")
                print("0. Return to main menu")

                sub_choice = input("Select an option: ")
                commands: Dict[str, Command] = {
                    "1": ViewManagersCommand(company),
                    "2": ViewInternsCommand(company),
                    "3": ViewVicePresidentsCommand(company),
                }

                command = commands.get(sub_choice)
                if command:
                    command.execute()
                elif sub_choice == "0":
                    break
                else:
                    print("Invalid option.")
                input("Press Enter to continue...")

        elif choice == "3":
            clear_screen()
            if not company.employees:
                print("No employees available.")
                input("Press Enter to continue...")
                continue

            for idx, emp in enumerate(company.employees):
                print(f"{idx}. {emp.get_info()}")
            try:
                idx = int(input("Select employee index: "))
                employee_to_vacation = company.get_employee_by_index(idx)
                payout = input("Payout instead of time off? (y/n): ").lower() == "y"
                command = TakeHolidayCommand(employee_to_vacation, payout, vacation_strategy)
                command.execute()
            except (IndexError, ValueError) as e:
                print(f"Error: {e}")
            input("Press Enter to continue...")

        elif choice == "4":
            clear_screen()
            if not company.employees:
                print("No employees available to pay.")
            else:
                command = PayAllEmployeesCommand(company, payment_strategies)
                command.execute()
            input("Press Enter to continue...")

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()