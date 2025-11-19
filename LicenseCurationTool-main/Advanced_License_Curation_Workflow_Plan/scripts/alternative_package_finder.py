#!/usr/bin/env python3
"""
Alternative Package Finder
Suggests alternative packages when license conflicts occur
"""

import requests
import json
import argparse
import sys
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import time


@dataclass
class AlternativePackage:
    """Information about an alternative package"""
    name: str
    version: str
    license: str
    package_type: str

    description: str
    homepage: str
    repository: str

    downloads_last_month: int
    github_stars: int
    last_updated: str

    compatibility_score: float
    popularity_score: float
    maintenance_score: float
    total_score: float

    reason_suggested: str

    def to_dict(self):
        return asdict(self)


class AlternativePackageFinder:
    """Find alternative packages with compatible licenses"""

    def __init__(self, policy_file: str = None):
        """Initialize finder with optional policy file"""
        self.policy = None
        if policy_file:
            import yaml
            with open(policy_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.policy = data['company_license_policy']

        # API endpoints
        self.pypi_api = 'https://pypi.org/pypi'
        self.npm_api = 'https://registry.npmjs.org'
        self.github_api = 'https://api.github.com'

        # Rate limiting
        self.last_request_time = {}

    def _rate_limit(self, api_name: str, min_interval: float = 0.1):
        """Simple rate limiting"""
        if api_name in self.last_request_time:
            elapsed = time.time() - self.last_request_time[api_name]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)

        self.last_request_time[api_name] = time.time()

    def find_alternatives(self,
                         package_name: str,
                         package_type: str,
                         forbidden_license: str,
                         approved_licenses: List[str],
                         max_results: int = 5) -> List[AlternativePackage]:
        """
        Find alternative packages with approved licenses

        Args:
            package_name: Name of package to replace
            package_type: Package type (PyPI, NPM, Maven)
            forbidden_license: The forbidden license to avoid
            approved_licenses: List of approved licenses to prefer
            max_results: Maximum number of alternatives to return

        Returns:
            List of AlternativePackage objects ranked by score
        """
        print(f"🔍 Searching for alternatives to {package_type}::{package_name}")
        print(f"   Avoiding license: {forbidden_license}")
        print(f"   Preferred licenses: {', '.join(approved_licenses[:3])}...")

        alternatives = []

        if package_type == 'PyPI':
            alternatives = self._search_pypi_alternatives(
                package_name, approved_licenses, max_results
            )
        elif package_type == 'NPM':
            alternatives = self._search_npm_alternatives(
                package_name, approved_licenses, max_results
            )
        else:
            print(f"⚠️  Package type '{package_type}' not yet supported")
            return []

        # Rank by total score
        alternatives.sort(key=lambda x: x.total_score, reverse=True)

        return alternatives[:max_results]

    def _search_pypi_alternatives(self,
                                  package_name: str,
                                  approved_licenses: List[str],
                                  max_results: int) -> List[AlternativePackage]:
        """Search PyPI for alternative packages"""
        alternatives = []

        # Strategy 1: Get package info to understand what it does
        try:
            pkg_info = self._get_pypi_package_info(package_name)
            keywords = self._extract_keywords(pkg_info)
            category = self._extract_category(pkg_info)

            print(f"   Keywords: {', '.join(keywords[:5])}")
            print(f"   Category: {category}")
        except Exception as e:
            print(f"   ⚠️  Could not fetch package info: {e}")
            keywords = [package_name]
            category = None

        # Strategy 2: Search for similar packages
        search_terms = self._build_search_terms(package_name, keywords, category)

        for search_term in search_terms[:3]:  # Limit searches
            try:
                search_results = self._search_pypi(search_term, max_results=20)

                for result in search_results:
                    pkg_name = result.get('name', '')

                    # Skip the original package
                    if pkg_name.lower() == package_name.lower():
                        continue

                    # Get detailed info
                    try:
                        pkg_detail = self._get_pypi_package_info(pkg_name)

                        # Check license
                        pkg_license = self._extract_pypi_license(pkg_detail)

                        # Only include if license is approved
                        if pkg_license in approved_licenses:
                            alt = self._create_pypi_alternative(
                                pkg_detail, pkg_license, approved_licenses
                            )

                            if alt and alt.total_score > 0:
                                alternatives.append(alt)

                    except Exception as e:
                        continue

            except Exception as e:
                print(f"   ⚠️  Search failed for '{search_term}': {e}")
                continue

        return alternatives

    def _get_pypi_package_info(self, package_name: str) -> Dict:
        """Get package info from PyPI API"""
        self._rate_limit('pypi', 0.1)

        url = f"{self.pypi_api}/{package_name}/json"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        return response.json()

    def _search_pypi(self, search_term: str, max_results: int = 20) -> List[Dict]:
        """Search PyPI (using simple search endpoint)"""
        self._rate_limit('pypi', 0.1)

        # PyPI doesn't have official search API, use RSS or scraping
        # For simplicity, we'll use a basic approach
        # In production, consider using libraries.io API or similar

        url = f"https://pypi.org/search/?q={search_term}"
        # Note: This is a simplified version. Real implementation should
        # use proper PyPI search API or libraries.io

        # Return mock results for demonstration
        # In production, parse search results
        return []

    def _extract_pypi_license(self, pkg_info: Dict) -> str:
        """Extract license from PyPI package info"""
        info = pkg_info.get('info', {})

        # Try license field
        license_field = info.get('license', '')
        if license_field and license_field != 'UNKNOWN':
            return self._normalize_license(license_field)

        # Try classifiers
        classifiers = info.get('classifiers', [])
        for classifier in classifiers:
            if classifier.startswith('License :: OSI Approved ::'):
                license_name = classifier.replace('License :: OSI Approved :: ', '')
                return self._normalize_license(license_name)

        return 'UNKNOWN'

    def _normalize_license(self, license_str: str) -> str:
        """Normalize license string to SPDX identifier"""
        mappings = {
            'MIT License': 'MIT',
            'Apache Software License': 'Apache-2.0',
            'BSD License': 'BSD-3-Clause',
            'GNU General Public License v3 (GPLv3)': 'GPL-3.0-only',
            'GNU General Public License v3 or later (GPLv3+)': 'GPL-3.0-or-later',
            'Mozilla Public License 2.0 (MPL 2.0)': 'MPL-2.0',
        }

        return mappings.get(license_str, license_str)

    def _extract_keywords(self, pkg_info: Dict) -> List[str]:
        """Extract keywords from package info"""
        info = pkg_info.get('info', {})

        keywords = []

        # From keywords field
        keywords_field = info.get('keywords', '')
        if keywords_field:
            keywords.extend([k.strip() for k in keywords_field.split(',')])

        # From summary/description
        summary = info.get('summary', '')
        if summary:
            # Extract important words (simple approach)
            words = summary.split()
            keywords.extend([w.strip('.,;:') for w in words if len(w) > 4])

        return list(set(keywords))[:10]

    def _extract_category(self, pkg_info: Dict) -> Optional[str]:
        """Extract category from classifiers"""
        info = pkg_info.get('info', {})
        classifiers = info.get('classifiers', [])

        for classifier in classifiers:
            if classifier.startswith('Topic :: '):
                return classifier.replace('Topic :: ', '')

        return None

    def _build_search_terms(self, package_name: str,
                           keywords: List[str],
                           category: Optional[str]) -> List[str]:
        """Build search terms for finding alternatives"""
        search_terms = []

        # Use keywords
        for keyword in keywords[:5]:
            search_terms.append(keyword)

        # Use category
        if category:
            search_terms.append(category.split(' :: ')[0])

        # Use package name parts
        name_parts = package_name.replace('-', ' ').replace('_', ' ').split()
        for part in name_parts:
            if len(part) > 3:
                search_terms.append(part)

        return list(set(search_terms))

    def _create_pypi_alternative(self,
                                 pkg_info: Dict,
                                 pkg_license: str,
                                 approved_licenses: List[str]) -> Optional[AlternativePackage]:
        """Create AlternativePackage from PyPI info"""
        info = pkg_info.get('info', {})

        name = info.get('name', '')
        version = info.get('version', '')
        description = info.get('summary', '')
        homepage = info.get('home_page', '')

        # Get repository from project_urls
        project_urls = info.get('project_urls', {})
        repository = project_urls.get('Source', '') or project_urls.get('Repository', '')

        # Get download stats (not available directly from PyPI API)
        # Would need to use pypistats API or libraries.io
        downloads = 0  # Placeholder

        # Get GitHub stars if repository is GitHub
        github_stars = 0
        if 'github.com' in repository:
            github_stars = self._get_github_stars(repository)

        # Get last updated
        releases = pkg_info.get('releases', {})
        if version in releases:
            release_info = releases[version]
            if release_info:
                upload_time = release_info[0].get('upload_time_iso_8601', '')
                last_updated = upload_time.split('T')[0] if upload_time else ''
            else:
                last_updated = ''
        else:
            last_updated = ''

        # Calculate scores
        compatibility_score = self._calculate_compatibility_score(
            pkg_license, approved_licenses
        )
        popularity_score = self._calculate_popularity_score(downloads, github_stars)
        maintenance_score = self._calculate_maintenance_score(last_updated)

        # Get weights from policy
        weights = {
            'license_compatibility': 0.40,
            'popularity': 0.25,
            'maintenance': 0.20
        }

        if self.policy:
            weights = self.policy.get('alternative_package_preferences', {}).get(
                'ranking_weights', weights
            )

        total_score = (
            compatibility_score * weights.get('license_compatibility', 0.4) +
            popularity_score * weights.get('popularity', 0.25) +
            maintenance_score * weights.get('maintenance', 0.20)
        )

        reason = f"Similar functionality with approved license ({pkg_license})"

        return AlternativePackage(
            name=name,
            version=version,
            license=pkg_license,
            package_type='PyPI',
            description=description,
            homepage=homepage,
            repository=repository,
            downloads_last_month=downloads,
            github_stars=github_stars,
            last_updated=last_updated,
            compatibility_score=compatibility_score,
            popularity_score=popularity_score,
            maintenance_score=maintenance_score,
            total_score=total_score,
            reason_suggested=reason
        )

    def _get_github_stars(self, repo_url: str) -> int:
        """Get GitHub stars for repository"""
        try:
            # Extract owner/repo from URL
            parts = repo_url.rstrip('/').split('/')
            if len(parts) >= 2:
                owner = parts[-2]
                repo = parts[-1].replace('.git', '')

                self._rate_limit('github', 1.0)

                url = f"{self.github_api}/repos/{owner}/{repo}"
                response = requests.get(url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    return data.get('stargazers_count', 0)
        except:
            pass

        return 0

    def _calculate_compatibility_score(self,
                                       license_str: str,
                                       approved_licenses: List[str]) -> float:
        """Calculate license compatibility score (0-1)"""
        if license_str in approved_licenses:
            # Prefer more permissive licenses
            permissive = ['MIT', 'Apache-2.0', 'BSD-2-Clause', 'BSD-3-Clause', 'ISC']
            if license_str in permissive:
                return 1.0
            else:
                return 0.8

        return 0.0

    def _calculate_popularity_score(self,
                                   downloads: int,
                                   github_stars: int) -> float:
        """Calculate popularity score (0-1)"""
        # Normalize using logarithmic scale
        import math

        download_score = min(math.log10(downloads + 1) / 7, 1.0)  # 10M downloads = 1.0
        stars_score = min(math.log10(github_stars + 1) / 5, 1.0)  # 100k stars = 1.0

        return (download_score * 0.6 + stars_score * 0.4)

    def _calculate_maintenance_score(self, last_updated: str) -> float:
        """Calculate maintenance score based on last update (0-1)"""
        if not last_updated:
            return 0.5

        try:
            last_update_date = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
            days_since_update = (datetime.now() - last_update_date.replace(tzinfo=None)).days

            if days_since_update < 30:
                return 1.0
            elif days_since_update < 90:
                return 0.9
            elif days_since_update < 180:
                return 0.7
            elif days_since_update < 365:
                return 0.5
            else:
                return 0.3
        except:
            return 0.5

    def _search_npm_alternatives(self,
                                package_name: str,
                                approved_licenses: List[str],
                                max_results: int) -> List[AlternativePackage]:
        """Search NPM for alternative packages"""
        # Similar implementation to PyPI
        # Would use NPM search API
        return []

    def generate_html_report(self,
                           original_package: str,
                           forbidden_license: str,
                           alternatives: List[AlternativePackage],
                           output_file: str):
        """Generate HTML report with alternative suggestions"""

        if not alternatives:
            print("⚠️  No alternatives found")
            return

        alt_rows = ""
        for i, alt in enumerate(alternatives, 1):
            score_color = self._get_score_color(alt.total_score)

            alt_rows += f"""
            <tr>
                <td>{i}</td>
                <td>
                    <strong>{alt.name}</strong>
                    <div class="version">v{alt.version}</div>
                </td>
                <td><span class="badge badge-success">{alt.license}</span></td>
                <td class="description">{alt.description}</td>
                <td>
                    <div class="score-bar">
                        <div class="score-fill" style="width: {alt.total_score * 100}%; background: {score_color};">
                            {alt.total_score:.2f}
                        </div>
                    </div>
                    <div class="score-details">
                        License: {alt.compatibility_score:.2f} |
                        Popularity: {alt.popularity_score:.2f} |
                        Maintenance: {alt.maintenance_score:.2f}
                    </div>
                </td>
                <td>
                    <div class="links">
                        {f'<a href="{alt.homepage}" target="_blank">🏠 Homepage</a><br>' if alt.homepage else ''}
                        {f'<a href="{alt.repository}" target="_blank">📦 Repository</a><br>' if alt.repository else ''}
                        <a href="https://pypi.org/project/{alt.name}/" target="_blank">📚 PyPI</a>
                    </div>
                </td>
                <td>
                    <div class="stats">
                        ⭐ {alt.github_stars:,} stars<br>
                        📅 {alt.last_updated}
                    </div>
                </td>
            </tr>
            """

        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alternative Packages for {original_package}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
            color: white;
            padding: 40px;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 15px;
        }}

        .warning-box {{
            background: rgba(255,255,255,0.2);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }}

        .content {{
            padding: 40px;
        }}

        .section-title {{
            font-size: 1.8em;
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        td {{
            padding: 15px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: top;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .version {{
            color: #6c757d;
            font-size: 0.9em;
            margin-top: 5px;
        }}

        .description {{
            max-width: 300px;
            font-size: 0.95em;
            color: #495057;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
            color: white;
        }}

        .badge-success {{ background: #28a745; }}
        .badge-danger {{ background: #dc3545; }}

        .score-bar {{
            width: 100%;
            height: 25px;
            background: #e9ecef;
            border-radius: 12px;
            overflow: hidden;
            margin-bottom: 5px;
        }}

        .score-fill {{
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 0.85em;
            transition: width 0.3s;
        }}

        .score-details {{
            font-size: 0.8em;
            color: #6c757d;
        }}

        .links a {{
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
        }}

        .links a:hover {{
            text-decoration: underline;
        }}

        .stats {{
            font-size: 0.9em;
            color: #495057;
        }}

        .footer {{
            padding: 30px;
            text-align: center;
            background: #f8f9fa;
            color: #6c757d;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>⚠️ Alternative Package Recommendations</h1>

            <div class="warning-box">
                <h3>❌ Forbidden License Detected</h3>
                <p><strong>Package:</strong> {original_package}</p>
                <p><strong>License:</strong> {forbidden_license}</p>
                <p><strong>Reason:</strong> This license is not approved for use in company products</p>
            </div>
        </div>

        <div class="content">
            <h2 class="section-title">✅ Recommended Alternatives ({len(alternatives)} found)</h2>

            <p style="margin-bottom: 20px; color: #6c757d;">
                The following packages provide similar functionality with approved licenses.
                Packages are ranked by compatibility, popularity, and maintenance status.
            </p>

            <table>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Package</th>
                        <th>License</th>
                        <th>Description</th>
                        <th>Score</th>
                        <th>Links</th>
                        <th>Stats</th>
                    </tr>
                </thead>
                <tbody>
                    {alt_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p><strong>Next Steps:</strong></p>
            <p>1. Review alternatives above</p>
            <p>2. Test functionality compatibility</p>
            <p>3. Replace forbidden package in dependencies</p>
            <p>4. Update imports and code if needed</p>
            <p>5. Re-run license compliance check</p>
        </div>
    </div>
</body>
</html>
"""

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Alternative packages report generated: {output_file}")

    def _get_score_color(self, score: float) -> str:
        """Get color for score visualization"""
        if score >= 0.8:
            return '#28a745'
        elif score >= 0.6:
            return '#ffc107'
        else:
            return '#dc3545'


def main():
    parser = argparse.ArgumentParser(
        description='Alternative Package Finder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Find PyPI alternatives
  python alternative_package_finder.py \\
    --package "pycutest" \\
    --type "PyPI" \\
    --forbidden-license "GPL-3.0-or-later" \\
    --approved "MIT,Apache-2.0,BSD-3-Clause" \\
    --output alternatives-pycutest.html

  # With policy file
  python alternative_package_finder.py \\
    --package "some-package" \\
    --type "PyPI" \\
    --policy config/company-policy.yml \\
    --output alternatives.html
        """
    )

    parser.add_argument('--package', required=True, help='Package name to replace')
    parser.add_argument('--type', required=True, choices=['PyPI', 'NPM'], help='Package type')
    parser.add_argument('--forbidden-license', required=True, help='Forbidden license to avoid')
    parser.add_argument('--approved', help='Comma-separated list of approved licenses')
    parser.add_argument('--policy', help='Policy file (optional)')
    parser.add_argument('--output', default='alternatives.html', help='Output HTML file')
    parser.add_argument('--max-results', type=int, default=5, help='Max alternatives to find')

    args = parser.parse_args()

    # Parse approved licenses
    if args.approved:
        approved_licenses = [l.strip() for l in args.approved.split(',')]
    elif args.policy:
        # Extract from policy
        import yaml
        with open(args.policy, 'r') as f:
            policy = yaml.safe_load(f)['company_license_policy']

        approved_licenses = []
        for category in policy['approved_licenses'].values():
            approved_licenses.extend(category['licenses'])
    else:
        print("❌ Must provide either --approved or --policy")
        sys.exit(1)

    print("🔍 Alternative Package Finder")
    print("=" * 60)

    # Initialize finder
    finder = AlternativePackageFinder(args.policy)

    # Find alternatives
    alternatives = finder.find_alternatives(
        package_name=args.package,
        package_type=args.type,
        forbidden_license=args.forbidden_license,
        approved_licenses=approved_licenses,
        max_results=args.max_results
    )

    print()
    print(f"✅ Found {len(alternatives)} alternatives")

    if alternatives:
        print()
        print("Top 3 recommendations:")
        for i, alt in enumerate(alternatives[:3], 1):
            print(f"  {i}. {alt.name} ({alt.license}) - Score: {alt.total_score:.2f}")

        # Generate report
        finder.generate_html_report(
            original_package=f"{args.type}::{args.package}",
            forbidden_license=args.forbidden_license,
            alternatives=alternatives,
            output_file=args.output
        )
    else:
        print("⚠️  No alternatives found. Manual search required.")

    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
