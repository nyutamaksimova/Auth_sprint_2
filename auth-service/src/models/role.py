from enum import Enum


class UserRole(str, Enum):
    USER = "USER"
    MODERATOR = "MODERATOR"
    CONTENT_MANAGER = "CONTENT_MANAGER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class Permission(str, Enum):
    VIEW_MOVIES = "view_movies"

    RATE_MOVIES = "rate_movies"

    COMMENT_MOVIES = "comment_movies"

    DELETE_COMMENTS = "delete_comments"

    EDIT_MOVIES = "edit_movies"

    CREATE_MOVIES = "create_movies"

    DELETE_MOVIES = "delete_movies"

    MANAGE_USERS = "manage_users"

    ASSIGN_ROLES = "assign_roles"

    VIEW_STATS = "view_stats"


ROLE_PERMISSIONS = {

    UserRole.USER: {
        Permission.VIEW_MOVIES,
        Permission.RATE_MOVIES,
        Permission.COMMENT_MOVIES,
    },

    UserRole.MODERATOR: {
        Permission.DELETE_COMMENTS,
    },

    UserRole.CONTENT_MANAGER: {
        Permission.CREATE_MOVIES,
        Permission.EDIT_MOVIES,
        Permission.DELETE_MOVIES,
    },

    UserRole.ADMIN: {
        Permission.MANAGE_USERS,
        Permission.ASSIGN_ROLES,
        Permission.VIEW_STATS,
    },

    UserRole.SUPER_ADMIN: {
        Permission.VIEW_MOVIES,
        Permission.RATE_MOVIES,
        Permission.COMMENT_MOVIES,
        Permission.DELETE_COMMENTS,
        Permission.CREATE_MOVIES,
        Permission.EDIT_MOVIES,
        Permission.DELETE_MOVIES,
        Permission.MANAGE_USERS,
        Permission.ASSIGN_ROLES,
        Permission.VIEW_STATS,
    }
}