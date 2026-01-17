from django.db import models
from users.models import User
from music.models import Song, Album
from distribution.models import DistributionRequest, Platform, RevenueSplit
from analytics.models import WithdrawalRequest

# 1. Artist Management
class Artist(User):
    class Meta:
        proxy = True
        verbose_name = "Artist"
        verbose_name_plural = "Artists"

class ArtistSong(Song):
    class Meta:
        proxy = True
        verbose_name = "Song"
        verbose_name_plural = "Songs"

class ArtistAlbum(Album):
    class Meta:
        proxy = True
        verbose_name = "Album"
        verbose_name_plural = "Albums"

class ArtistRevenueSplit(RevenueSplit):
    class Meta:
        proxy = True
        verbose_name = "Revenue Split"
        verbose_name_plural = "Revenue Splits"

# 2. Release Management
# 2. Release Management
from distribution.models import ReleaseRequest as DistReleaseRequest

class ReleaseRequest(DistReleaseRequest):
    class Meta:
        proxy = True
        verbose_name = "Release Request"
        verbose_name_plural = "Release Requests"

# 3. Finance
class PayoutRequest(WithdrawalRequest):
    class Meta:
        proxy = True
        verbose_name = "Payout Request"
        verbose_name_plural = "Payout Requests"

# 4. Platform Management
class PlatformSettings(Platform):
    class Meta:
        proxy = True
        verbose_name = "Platform"
        verbose_name_plural = "Platforms"

# 5. User Management
class SystemUser(User):
    class Meta:
        proxy = True
        verbose_name = "System User"
        verbose_name_plural = "System Users"

# 6. Investment Management
from investments.models import InvestmentProduct as InvProduct

class InvestmentProduct(InvProduct):
    class Meta:
        proxy = True
        verbose_name = "Investment Product"
        verbose_name_plural = "Investment Products"
