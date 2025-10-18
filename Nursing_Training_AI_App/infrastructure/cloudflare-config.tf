# Terraform configuration for CloudFlare CDN
# Handles DNS, SSL, caching, and DDoS protection

terraform {
  required_providers {
    cloudflare = {
      source  = "cloudflare/cloudflare"
      version = "~> 4.0"
    }
  }
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}

variable "cloudflare_api_token" {
  description = "CloudFlare API Token"
  type        = string
  sensitive   = true
}

variable "zone_id" {
  description = "CloudFlare Zone ID for nursingtrainingai.com"
  type        = string
}

variable "origin_server_ip" {
  description = "Origin server IP address"
  type        = string
}

# DNS Records
resource "cloudflare_record" "root" {
  zone_id = var.zone_id
  name    = "nursingtrainingai.com"
  value   = var.origin_server_ip
  type    = "A"
  proxied = true  # Enable CDN
}

resource "cloudflare_record" "www" {
  zone_id = var.zone_id
  name    = "www"
  value   = "nursingtrainingai.com"
  type    = "CNAME"
  proxied = true
}

resource "cloudflare_record" "api" {
  zone_id = var.zone_id
  name    = "api"
  value   = var.origin_server_ip
  type    = "A"
  proxied = true
}

resource "cloudflare_record" "app" {
  zone_id = var.zone_id
  name    = "app"
  value   = var.origin_server_ip
  type    = "A"
  proxied = true
}

# SSL/TLS Configuration
resource "cloudflare_zone_settings_override" "ssl" {
  zone_id = var.zone_id

  settings {
    # SSL Mode
    ssl = "strict"
    
    # Always use HTTPS
    always_use_https = "on"
    
    # Minimum TLS version
    min_tls_version = "1.2"
    
    # TLS 1.3
    tls_1_3 = "on"
    
    # Automatic HTTPS Rewrites
    automatic_https_rewrites = "on"
    
    # HTTP/2
    http2 = "on"
    
    # HTTP/3 (QUIC)
    http3 = "on"
    
    # Brotli compression
    brotli = "on"
  }
}

# Page Rules for caching
resource "cloudflare_page_rule" "api_no_cache" {
  zone_id = var.zone_id
  target  = "api.nursingtrainingai.com/*"
  priority = 1
  
  actions {
    cache_level = "bypass"  # Don't cache API responses
  }
}

resource "cloudflare_page_rule" "static_cache" {
  zone_id = var.zone_id
  target  = "*.nursingtrainingai.com/static/*"
  priority = 2
  
  actions {
    cache_level = "cache_everything"
    edge_cache_ttl = 86400  # 24 hours
    browser_cache_ttl = 3600  # 1 hour
  }
}

resource "cloudflare_page_rule" "assets_cache" {
  zone_id = var.zone_id
  target  = "*.nursingtrainingai.com/assets/*"
  priority = 3
  
  actions {
    cache_level = "cache_everything"
    edge_cache_ttl = 604800  # 7 days
    browser_cache_ttl = 86400  # 24 hours
  }
}

# Rate Limiting
resource "cloudflare_rate_limit" "api_rate_limit" {
  zone_id = var.zone_id
  
  threshold = 100
  period = 60  # per minute
  
  match {
    request {
      url_pattern = "api.nursingtrainingai.com/*"
    }
  }
  
  action {
    mode = "challenge"
    timeout = 3600
  }
  
  description = "API rate limit - 100 requests per minute"
}

# Firewall Rules
resource "cloudflare_filter" "block_bad_bots" {
  zone_id = var.zone_id
  description = "Block known bad bots"
  expression = "(cf.client.bot) and not (cf.verified_bot_category in {\"Search Engine Crawler\" \"Page Preview\"})"
}

resource "cloudflare_firewall_rule" "block_bad_bots" {
  zone_id = var.zone_id
  description = "Block bad bots"
  filter_id = cloudflare_filter.block_bad_bots.id
  action = "block"
}

# WAF (Web Application Firewall)
resource "cloudflare_waf_group" "owasp" {
  zone_id = var.zone_id
  package_id = "a25a9a7e9c00afc1fb2e0245519d725d"  # OWASP Core RuleSet
  mode = "on"
}

# DDoS Protection (Enterprise feature)
resource "cloudflare_zone_lockdown" "api_lockdown" {
  zone_id = var.zone_id
  description = "Lockdown API to known IPs only (optional)"
  
  urls = [
    "api.nursingtrainingai.com/api/admin/*"
  ]
  
  configurations {
    target = "ip"
    value = "YOUR_OFFICE_IP/32"
  }
}

# Load Balancing (if using multiple origin servers)
resource "cloudflare_load_balancer_pool" "origin_pool" {
  name = "nursing-ai-origin-pool"
  
  origins {
    name = "origin-1"
    address = var.origin_server_ip
    enabled = true
  }
  
  # Health check
  check_regions = ["WEU"]  # Western Europe
  
  monitor = cloudflare_load_balancer_monitor.http_monitor.id
}

resource "cloudflare_load_balancer_monitor" "http_monitor" {
  expected_codes = "200"
  method = "GET"
  path = "/api/health"
  interval = 60
  retries = 2
  timeout = 5
  type = "http"
}

resource "cloudflare_load_balancer" "lb" {
  zone_id = var.zone_id
  name = "nursing-ai-lb"
  default_pool_ids = [cloudflare_load_balancer_pool.origin_pool.id]
  fallback_pool_id = cloudflare_load_balancer_pool.origin_pool.id
  proxied = true
  
  # Geo steering
  region_pools {
    region = "WEUR"
    pool_ids = [cloudflare_load_balancer_pool.origin_pool.id]
  }
}

# Outputs
output "nameservers" {
  value = "Set your domain nameservers to CloudFlare"
}

output "ssl_status" {
  value = "SSL/TLS will be automatically provisioned"
}

