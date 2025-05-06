# Handloom Supply Chain Management System

A Django-based system for tracking thread consumption, production activity, and inventory management in the handloom supply chain. This system provides comprehensive analytics and reporting features to improve visibility and traceability.

## Features

### Core Features
- Dashboard with real-time statistics and analytics
- Thread batch management and tracking
- Production log tracking with issue reporting
- Loom assignment and status management
- Weaver performance monitoring
- Inventory management system
- User authentication and role-based access
- Responsive Bootstrap 5.3 UI with modern design

### Analytics & Reporting
- Weaver performance analytics
- Top productive looms tracking
- Production trends visualization
- Inventory status monitoring
- Thread utilization analysis
- Low production alerts
- Thread consumption reporting
- Production heatmap
- Loom efficiency metrics
- Data export capabilities (CSV)

## Prerequisites

- Python 3.11+
- Conda (for environment management)
- Required packages:
  - Django
  - django-crispy-forms
  - crispy-bootstrap5
  - django-cors-headers
  - django-filter
  - djangorestframework
  - python-dotenv

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd handloom
   ```

2. Create and activate Conda environment:
   ```bash
   conda create -n handloom python=3.11
   conda activate handloom
   ```

3. Install dependencies:
   ```bash
   conda install -c conda-forge django django-crispy-forms crispy-bootstrap5 django-cors-headers django-filter djangorestframework python-dotenv
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Generate sample data (optional):
   ```bash
   python manage.py generate_sample_data
   ```

7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

### Core Components
- `supplychain/` - Main application directory
  - `models.py` - Database models (Weaver, Loom, ThreadBatch, ProductionLog, Inventory)
  - `views.py` - View functions and API endpoints
  - `forms.py` - Forms with Bootstrap styling
  - `admin.py` - Admin interface customization
  - `urls.py` - URL routing
  - `analytics.py` - Analytics and reporting functions

### Templates
- `templates/` - HTML templates
  - `base.html` - Base template with navigation
  - `supplychain/`
    - `dashboard.html` - Main dashboard
    - `weaver_*.html` - Weaver management templates
    - `loom_*.html` - Loom management templates
    - `production_*.html` - Production tracking templates
    - `inventory_*.html` - Inventory management templates
    - `analytics/` - Analytics templates
      - `weaver_performance.html`
      - `top_looms.html`
      - `production_trends.html`
      - `inventory_status.html`

## Features in Detail

### Dashboard
- Total weavers and active count
- Active looms and maintenance status
- Thread batches in inventory
- Total production metrics
- Recent activities feed
- Quick access to analytics

### Inventory Management
- Track multiple material types:
  - Yarn (Cotton, Silk, Wool, etc.)
  - Dyes (Various colors)
  - Chemicals
  - Finished Products
- Monitor stock levels
- Set minimum quantity thresholds
- Track supplier information
- Value calculation
- Stock status indicators

### Production Management
- Daily production logging
- Issue tracking and reporting
- Thread batch association
- Efficiency calculations
- Production trends analysis

### Analytics & Reports
- Weaver Performance:
  - Daily production metrics
  - Efficiency ratios
  - Skill level tracking
- Loom Analytics:
  - Top productive looms
  - Efficiency metrics
  - Maintenance tracking
- Production Analysis:
  - Daily/Monthly trends
  - Heatmap visualization
  - Thread utilization
- Inventory Analytics:
  - Stock level monitoring
  - Value analysis
  - Usage patterns

### Data Export
- Export production logs to CSV
- Export thread batch data
- Custom report generation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 