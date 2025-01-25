#!/bin/sh

# Update these constants at the top
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/mb/clean"
MAX_BACKUPS=3  # Keep at 3 as in the current version
mkdir -p "$CACHE_DIR"

# Function to display usage
mbclean_usage() {
    cat <<EOF
Usage: mbclean [OPTION] [SEARCH_PATH] 

Clean up project directories by removing temporary and compiled artifacts while backing up important files.

Options:
  -a, --all           Clean all artifacts including build artifacts.
  -d, --dry-run       Perform a dry run without deleting any files.
  -h, --help          Show this help message and exit.
  -f, --force         Force clean directories other than the default patterns.

  -p, --pattern       Specify a custom pattern to clean. 
                      Default patterns are:
                      - *.pyc, *.pyo, __pycache__, *.tmp, *.log, *.bak, *.swp, .DS_Store

                      Default patterns for --all:
                      - build/, dist/, *.egg-info, *.dist-info, *.o, *.so

Arguments:
  SEARCH_PATH         Path to search for artifacts. Default is the current directory.
Examples:
  mbclean -a .        Clean all artifacts in the current directory and subdirectories.
  mbclean -a "*.log"  Clean all log files (*.log) and their backups.

Backup Information:
  - Backups are stored in: ${CACHE_DIR}
  - A maximum of ${MAX_BACKUPS} backups are retained. Older backups are deleted automatically.
EOF
}

# Function to backup non-junk files
backup_file() {
    local file="$1"
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="$CACHE_DIR/backup_$timestamp"
    local backup_path="$backup_dir/$(echo "$file" | sed 's|^./||')"

    mkdir -p "$(dirname "$backup_path")"

    # Define junk patterns
    local junk_patterns="*.pyc *.pyo __pycache__ *.tmp *.log *.bak *.swp .DS_Store build/ dist/ *.egg-info *.dist-info *.o *.so"

    # Check if file is junk and skip backup
    for pattern in $junk_patterns; do
        case "$file" in
            $pattern)
                return 0
                ;;
        esac
    done

    if [ -d "$file" ]; then
        if cp -r "$file" "$backup_path"; then
            return 0
        else
            echo "Failed to backup directory: $file" >&2
            return 1
        fi
    elif [ -f "$file" ]; then
        if cp "$file" "$backup_path"; then
            return 0
        else
            echo "Failed to backup file: $file" >&2
            return 1
        fi
    else
        echo "Skipping: $file (not a file or directory)" >&2
        return 1
    fi
}

# Function to clean up old backups
cleanup_old_backups() {
    local backup_count
    backup_count=$(ls -d "$CACHE_DIR"/backup_* 2>/dev/null | wc -l)
    if [ "$backup_count" -gt "$MAX_BACKUPS" ]; then
        local to_remove=$((backup_count - MAX_BACKUPS))
        ls -d "$CACHE_DIR"/backup_* | sort | head -n "$to_remove" | xargs -r rm -rf
        echo "Removed $to_remove old backup(s)"
        # echo "Remaining backups: $(ls -d "$CACHE_DIR"/backup_*)"
    fi
}


# Main script
SEARCH_PATH="."
CUSTOM_PATTERN=""
CLEAN_BUILD=""
DRY_RUN=""
FORCE_CLEAN=""
patterns=()
clean_artifacts() {
    cleanup_old_backups &
    CLEANUP_PID=$!
    temp_status=$(mktemp)
    find_args=()
    if [ -n "$patterns" ]; then
        find_args+=( -name "${patterns[0]}" )
        for pattern in "${patterns[@]:1}"; do
            find_args+=( -o -name "$pattern" )
        done
    fi
    if [ -n "$CUSTOM_PATTERN" ]; then
        find_args+=( -name "$CUSTOM_PATTERN" -o )
    fi
    find_args+=( \
        -name "*.pyc" -o \
        -name "*.pyo" -o \
        -name "__pycache__" -o \
        -name "*.tmp" -o \
        -name "*.bak" -o \
        -name "*.swp" -o \
        -name ".DS_Store" \
     )
    if [ -n "$CLEAN_BUILD" ]; then
        find_args+=(\
            -o \
            -name "build" -o \
            -name "dist" -o \
            -name "*.egg-info" -o \
            -name "*.dist-info" -o \
            -name "*.o" -o \
            -name "*.so" 
        )
    fi
    find "$SEARCH_PATH" "${find_args[@]}" ! -path '*/.venv/*' ! -path '*/site-packages/*' | while read -r file; do
        case "$file" in
            *venv*|*site-packages*)
                continue
                ;;
            *.pyc|*.pyo|*__pycache__|*.tmp|*.log|*.bak|*.swp|*.DS_Store*|*build|*dist|*.egg-info|*.dist-info|*.o|*.so|*tmp|*log|*bak|*swp|*DS_Store)
                ;;
            *)
                if [ -d "$file" ] && [ -z "$FORCE_CLEAN" ]; then
                    echo "Directory matched: $file. Skipping. Pass -f to force clean."
                    continue
                fi
                ;;
        esac

        if [ -d "$file" ]; then
            if backup_file "$file"; then
                if [ -n "$DRY_RUN" ]; then
                    echo "Dry run: Would have removed directory: $file"
                else
                    echo "Removing directory: $file"
                    rm -rf "$file"
                fi
                if  [ -f "$temp_status" ]; then
                    rm -rf "$temp_status"
                fi
            else
                echo "Failed to backup directory: $file"
            fi

        elif [ -f "$file" ]; then
            if backup_file "$file"; then
                if [ -n "$DRY_RUN" ]; then
                    echo "Dry run: Would have removed: $file"
                else
                    echo "Removing: $file"
                    rm -f "$file"
                    
                fi
                if  [ -f "$temp_status" ]; then
                    rm -rf "$temp_status"
                fi
            else
                echo "Failed to backup file: $file"
            fi

        fi
    done
    if [ -f "$temp_status" ]; then
        rm -f "$temp_status"
        echo "All clean! ✨"
        kill "$CLEANUP_PID" 2>/dev/null
        return 0
    fi
    wait "$CLEANUP_PID"
    echo "Cleanup completed."
    return 0
 
}



while [ $# -gt 0 ]; do
    case "$1" in
        -f|--force)
            shift
            FORCE_CLEAN=1
            ;;
        -d|--dry-run)
            shift
            DRY_RUN=1
            ;;
        -a|--all)
            shift
            CLEAN_BUILD=1
            ;;
        -h|--help)
            mbclean_usage

            exit 0
            ;;
        -p|--pattern)
            shift
            CUSTOM_PATTERN="$1"
            if [ -z "$CUSTOM_PATTERN" ]; then
                echo "Error: Missing pattern argument" >&2
                exit 1
            fi
            patterns+=("$CUSTOM_PATTERN")
            shift   
            ;;
        *)
            SEARCH_PATH="$1"
            shift
            ;;
    esac
done

if [ -n "$DRY_RUN" ]; then
    echo "Dryn run: Cleaning artifacts in: $SEARCH_PATH for pattern: $CUSTOM_PATTERN with build: $CLEAN_BUILD"
fi
clean_artifacts

