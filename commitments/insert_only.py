import uuid

from django.db import models


class ActiveRuleManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(ts_end=None).exclude(op="D")


class VersionableModel(models.Model):
    oid = models.UUIDField(null=False, editable=False, db_index=True,
                           help_text="Object ID of the rule. Stable with different updates of the rule.")
    vid = models.UUIDField(null=False, editable=False, primary_key=True,
                           help_text="Unique ID of the version of the rule. Changes with each update.")
    ts = models.DateTimeField(blank=False, auto_now=True, editable=False, db_index=True,
                              help_text="The moment this version was created")
    ts_end = models.DateTimeField(blank=True, null=True, editable=False,
                                  help_text="The moment the rule is no longer is valid")
    op = models.CharField(max_length=1, null=False, default="A", editable=False,
                          help_text="Operation of this version",
    choices=[("C", "Create"), ("U", "Update"), ("D", "Delete")])


    ## The fields of your domain.
    objects = ActiveRuleManager()  # Only the currently active registers
    versions = models.Manager()  # All of the versions of registers.

    def __str__(self):
        #return f"{self.oid}/{self.vid} ({self.ts})"
        if self.op == "D":
            return f"DELETED {self.oid}"
        return f"{self.oid}"

    class Meta:
        abstract = True
        unique_together = (("ts_end", "oid"),)  # This ensures no rule can have two current versions.
        get_latest_by = "ts"

    def save(self, *args, **kwargs):
        self.vid = uuid.uuid4()  ## Make sure every save is a new entry
        if self.oid is None:  # no oid, means this is a new entry (not an update of an existing one)
            self.oid = uuid.uuid4()
            self.op = "A"
        else:  ## it's an update of an existing entry
            self.op = "U"
        super().save(force_insert=True, *args, **kwargs)  # Call the "real" save() method.

    def delete(self, using=None, keep_parents=False):
        self.vid = uuid.uuid4()  ## Force a new row.
        self.op = "D"  # Mark it as the final state of the Rule.
        super().save(force_insert=True)  # Call the "real" save() method.
        self.oid = None
