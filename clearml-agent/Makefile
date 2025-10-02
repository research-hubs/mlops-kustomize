# Clearml Agent - Cross-Platform Makefile
# Auto-detects OS and uses appropriate platform-specific Makefile

# Detect operating system
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    MAKEFILE_EXT := .win
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        DETECTED_OS := Linux
    endif
    ifeq ($(UNAME_S),Darwin)
        DETECTED_OS := macOS
    endif
    MAKEFILE_EXT := .unix
endif

# Colors (Unix only)
ifneq ($(OS),Windows_NT)
    YELLOW := \033[0;33m
    GREEN := \033[0;32m
    NC := \033[0m
else
    YELLOW := 
    GREEN := 
    NC := 
endif

# Default environment
ENV ?= development

# Check if platform-specific Makefile exists
PLATFORM_MAKEFILE := Makefile$(MAKEFILE_EXT)
ifeq (,$(wildcard $(PLATFORM_MAKEFILE)))
    $(error Platform-specific Makefile '$(PLATFORM_MAKEFILE)' not found for $(DETECTED_OS))
endif

.PHONY: help os-info

# Default target shows help
help: ## Show help for Clearml Agent
	@echo "$(GREEN)Clearml Agent - Cross-Platform Build ($(DETECTED_OS))$(NC)"
	@echo "$(YELLOW)Using: $(PLATFORM_MAKEFILE)$(NC)"
	@echo ""
	@$(MAKE) -f $(PLATFORM_MAKEFILE) help

os-info: ## Show OS detection info
	@echo "Detected OS: $(DETECTED_OS)"
	@echo "Using Makefile: $(PLATFORM_MAKEFILE)"

# Delegate all other targets to platform-specific Makefile
%:
	@$(MAKE) -f $(PLATFORM_MAKEFILE) $@ ENV=$(ENV)
