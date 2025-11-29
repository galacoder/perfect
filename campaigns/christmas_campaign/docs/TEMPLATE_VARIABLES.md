# Email Template Variables Reference

**Campaign**: Christmas 2025
**Last Updated**: 2025-11-28
**Source**: `campaigns/christmas_campaign/tasks/resend_operations.py:get_email_variables()`

---

## Overview

This document lists all template variables available for email personalization in the Christmas Campaign. Templates use Mustache-style syntax (`{{variable_name}}`) for variable substitution.

**Variable Sources**:
- Assessment data (from BusOS assessment)
- Contact data (name, business, email)
- Calculated values (revenue leak, tips, deadlines)
- Static configuration (calendly links, deadline dates)

---

## Core Contact Variables

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `first_name` | String | `Sarah` | Contact first name (default: "there") |
| `business_name` | String | `Sarah's Salon` | Business name (default: "your business") |

**Usage**:
```html
<p>Hi {{first_name}},</p>
<p>We reviewed {{business_name}} and found...</p>
```

---

## Assessment Score Variables

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `overall_score` | String | `52` | BusOS overall score (0-100) |
| `assessment_score` | String | `52` | Alias for `overall_score` |
| `segment` | String | `CRITICAL` | Contact segment: CRITICAL/URGENT/OPTIMIZE |
| `readiness_zone` | String | `Crisis Zone` | Zone based on segment (Crisis/Warning/Growth) |
| `red_systems` | String | `2` | Number of red (broken) systems |
| `orange_systems` | String | `1` | Number of orange (struggling) systems |
| `yellow_systems` | String | `2` | Number of yellow (functional) systems |
| `green_systems` | String | `3` | Number of green (optimized) systems |

**Readiness Zone Mapping**:
- CRITICAL → "Crisis Zone"
- URGENT → "Warning Zone"
- OPTIMIZE → "Growth Zone"

**Usage**:
```html
<p>Your BusOS Score: {{overall_score}}/100</p>
<p>You're in the {{readiness_zone}} with {{red_systems}} critical systems.</p>
```

---

## System Analysis Variables

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `weakest_system_1` | String | `GPS` | First weakest system name |
| `weakest_system_2` | String | `FUEL` | Second weakest system name |
| `strongest_system` | String | `CABIN` | Strongest system name |
| `WeakestSystem1` | String | `GPS` | CamelCase alias for `weakest_system_1` |
| `WeakestSystem2` | String | `FUEL` | CamelCase alias for `weakest_system_2` |
| `StrongestSystem` | String | `CABIN` | CamelCase alias for `strongest_system` |
| `weakest_system` | String | `GPS` | Alias for `weakest_system_1` (for templates) |
| `gps_score` | Integer | `45` | GPS system score (optional) |
| `money_score` | Integer | `38` | Money system score (optional) |

**Usage**:
```html
<p>Your weakest system is {{WeakestSystem1}}, which is leaking revenue.</p>
<p>Focus on fixing {{weakest_system_1}} first.</p>
```

---

## Revenue Leak Variables

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `revenue_leak_total` | String | `14700` | Total revenue leak estimate (raw number) |
| `TotalRevenueLeak_K` | String | `15` | Revenue leak in thousands (rounded) |

**Usage**:
```html
<p>You're leaking ${{TotalRevenueLeak_K}}K/year in potential revenue.</p>
<p>Total estimated leak: ${{revenue_leak_total}}</p>
```

---

## Deadline & Urgency Variables

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `days_to_deadline` | String | `7` | Days remaining until December 5, 2025 |
| `deadline_date` | String | `December 5, 2025` | Deadline date (formatted) |
| `spots_remaining` | String | `12` | Dynamic spot counter for urgency |
| `bookings_count` | String | `18` | Number of bookings this week |

**Usage**:
```html
<p>Only {{days_to_deadline}} days left until {{deadline_date}}!</p>
<p>{{spots_remaining}} spots remaining for December diagnostic calls.</p>
```

---

## Personalized Tips Variables

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `personalized_tip_1` | String | `Map your customer journey...` | First tip (based on weakest system) |
| `personalized_tip_2` | String | `Write down 3 tasks...` | Second tip (based on second weakest) |
| `personalized_tip_3` | String | `Block 2 hours this weekend...` | Third tip (general holiday prep) |

**Tip Generation Logic**:
- Tips are generated based on `weakest_system_1` and `weakest_system_2`
- Each BusOS system has a corresponding actionable tip
- Tip 3 is always holiday-focused

**System-to-Tip Mapping**:
```
GPS   → "Map your customer journey from first contact to payment"
CREW  → "Write down 3 tasks someone else could do with a checklist"
ENGINE → "List your top 3 services by profit margin (not revenue)"
FUEL  → "Track where your last 10 clients came from"
CABIN → "Send a 'How are we doing?' text to 5 recent clients today"
COCKPIT → "Check if you know your exact profit margin per service"
RADAR → "Create a simple spreadsheet tracking daily bookings"
AUTOPILOT → "Identify 1 task you do manually that could be automated"
```

**Usage**:
```html
<ul>
  <li>{{personalized_tip_1}}</li>
  <li>{{personalized_tip_2}}</li>
  <li>{{personalized_tip_3}}</li>
</ul>
```

---

## Links & Resources

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `calendly_link` | String | `https://cal.com/sangletech/discovery-call` | Calendly booking link |
| `pdf_download_link` | String | `https://sangletech.com/.../assessment` | Assessment results page URL |
| `portal_url` | String | `https://portal.example.com/...` | Customer portal URL (optional) |

**Usage**:
```html
<a href="{{calendly_link}}">Book Your Discovery Call</a>
<a href="{{pdf_download_link}}">Download Your Results</a>
```

---

## Optional Variables

| Variable | Type | Example | Description |
|----------|------|---------|-------------|
| `diagnostic_call_date` | String | `2025-12-10T14:00:00Z` | Scheduled call date (ISO format) |

**Usage**:
```html
{{#diagnostic_call_date}}
<p>Your call is scheduled for {{diagnostic_call_date}}</p>
{{/diagnostic_call_date}}
```

---

## Variable Naming Conventions

**Case Sensitivity**:
- Most variables use `snake_case` (e.g., `first_name`, `weakest_system_1`)
- Some use `CamelCase` for template compatibility (e.g., `WeakestSystem1`, `TotalRevenueLeak_K`)
- Both formats are provided for key variables

**Default Values**:
- `first_name`: "there"
- `business_name`: "your business"
- Numeric values default to "0" or "N/A"
- System names default to "GPS" if not provided

---

## Template Examples

### Email 1 (Lead Nurture) - 12 Variables
```html
<p>Hi {{first_name}},</p>
<p>Your BusOS Score: {{overall_score}}/100</p>
<p>You're in the {{readiness_zone}}.</p>
<p>Your weakest system: {{WeakestSystem1}}</p>
<p>Revenue leak: ${{TotalRevenueLeak_K}}K/year</p>
<p>Quick tips:</p>
<ul>
  <li>{{personalized_tip_1}}</li>
  <li>{{personalized_tip_2}}</li>
</ul>
<a href="{{calendly_link}}">Book Discovery Call</a>
```

### Email 2 (Follow-Up) - 2 Variables
```html
<p>Hi {{first_name}},</p>
<p>Let's fix your {{WeakestSystem1}} system first.</p>
<a href="{{pdf_download_link}}">Review Your Results</a>
```

### Email 3-5 (Nurture Sequence) - Static or Minimal Variables
```html
<p>Hi {{first_name}},</p>
<p>Only {{days_to_deadline}} days left!</p>
<p>{{spots_remaining}} spots remaining.</p>
<a href="{{calendly_link}}">Claim Your Spot</a>
```

---

## Implementation Notes

**Variable Substitution**:
- Uses regex replacement: `{{variable_name}}` → actual value
- Performed in `resend_operations.py:substitute_variables()`
- Applied to BOTH subject line and HTML body

**Data Flow**:
1. Assessment data collected from website form
2. Variables calculated in `get_email_variables()`
3. Template fetched from Notion Email Templates DB
4. Variables substituted in template
5. Email sent via Resend API

**Error Handling**:
- Missing variables are replaced with empty strings (no error)
- Optional variables (e.g., `gps_score`) can be `None` → "N/A"
- Default values ensure templates always render

---

## Related Documentation

- **Variable Generation**: `campaigns/christmas_campaign/tasks/resend_operations.py`
- **Template Fetching**: `campaigns/christmas_campaign/tasks/notion_operations.py`
- **Email Sending**: `campaigns/christmas_campaign/flows/send_email_flow.py`
- **Segment Classification**: `campaigns/christmas_campaign/tasks/routing.py`

---

## Maintenance

**When adding new variables**:
1. Add parameter to `get_email_variables()` function
2. Add variable to returned dictionary
3. Update this documentation
4. Update Notion templates if needed
5. Test with sample data

**When updating defaults**:
1. Update default value in `get_email_variables()`
2. Update this documentation
3. Test edge cases (missing data, None values)

---

**Version**: 1.0
**Maintained by**: Christmas Campaign Team
