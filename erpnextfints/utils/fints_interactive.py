import frappe


def show_progressbar(
    message: str, docname: str, progress: float = 0, reload: bool = False
) -> None:
    """Show a progressbar on client side."""
    frappe.publish_realtime(
        "fints_progressbar",
        {
            "progress": progress,
            "docname": docname,
            "message": message,
            "reload": reload,
        },
        user=frappe.session.user,
    )
