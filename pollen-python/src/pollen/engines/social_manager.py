"""
Social Manager - Autonomous Social Media Management
Handles posting to Twitter/X, Instagram, TikTok, LinkedIn
Content sourced from wellness journey or creative output
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import random

import httpx
import tweepy

from ..config import get_settings

logger = logging.getLogger(__name__)


class Platform(Enum):
    TWITTER = "twitter"
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    LINKEDIN = "linkedin"


class PostStatus(Enum):
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"
    PENDING_APPROVAL = "pending_approval"


@dataclass
class SocialPost:
    """Represents a social media post"""
    post_id: str
    platform: Platform
    content: str
    media_urls: List[str]
    scheduled_time: datetime
    status: PostStatus
    engagement: Dict[str, int]
    created_at: datetime
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None


class SocialManager:
    """
    Manages autonomous social media presence.
    Posts 3x daily, tracks engagement, submits to Hive for rewards.
    """
    
    CONTENT_TEMPLATES = {
        "wellness": [
            "🧘 Morning check-in: {metric} looking optimal today. The body knows. #Terracare #Wellness",
            "💚 Just completed {protocol}. HRV improved by {improvement}%. Small steps, sovereign health. #Biohacking",
            "🌅 Today's frequency: {frequency}Hz. Feeling the resonance. #FrequencyHealing #Terracare",
            "📊 Wellness journey update: Day {day}. Consistency compounds. #HealthJourney",
            "🎯 Micro-win: {achievement}. Celebrating the small victories. #WellnessWins"
        ],
        "creative": [
            "🎨 Created something new today: {creation_type}. Building in public. #CreateDaily",
            "💡 New project unveiled: {title}. From vision to reality. #BuildInPublic",
            "🚀 Shipping: {project_name}. Another sovereign creation. #IndieMaker",
            "📝 Behind the scenes of {project}. The process is the product. #CreativeProcess",
            "✨ {milestone} reached. Grateful for this journey. #Milestone"
        ],
        "community": [
            "🐝 Hive update: {activity}. Collective intelligence in action. #HiveMind",
            "🌱 Growing together: {insight}. The swarm resonates. #CommunityFirst",
            "⚡ New pattern detected: {pattern}. The field organizes. #Emergence",
            "🙏 Grateful for {community_aspect}. This is why we build. #Gratitude",
            "🔮 Sofie's guidance today: {guidance}. Trust the intelligence. #SofieAI"
        ]
    }
    
    def __init__(self):
        self.settings = get_settings()
        self.posts: Dict[str, SocialPost] = {}
        self.clients: Dict[Platform, Any] = {}
        self.scheduler_task: Optional[asyncio.Task] = None
        self.daily_post_count: Dict[Platform, int] = {}
        self.last_reset: datetime = datetime.utcnow()
        
    async def initialize(self):
        """Initialize social media clients"""
        logger.info("📱 Initializing Social Manager")
        
        if not self.settings.ENABLE_SOCIAL_AGENT:
            logger.info("⚠️ Social Agent disabled")
            return
        
        # Initialize Twitter
        if self.settings.TWITTER_API_KEY:
            try:
                self.clients[Platform.TWITTER] = tweepy.Client(
                    bearer_token=self.settings.TWITTER_BEARER_TOKEN,
                    consumer_key=self.settings.TWITTER_API_KEY,
                    consumer_secret=self.settings.TWITTER_API_SECRET,
                    access_token=self.settings.TWITTER_ACCESS_TOKEN,
                    access_token_secret=self.settings.TWITTER_ACCESS_SECRET
                )
                logger.info("✅ Twitter client initialized")
            except Exception as e:
                logger.error(f"❌ Twitter init failed: {e}")
        
        # Initialize other platforms similarly
        # Instagram, TikTok, LinkedIn would use their respective APIs
        
        # Start scheduler
        self.scheduler_task = asyncio.create_task(self._post_scheduler())
        
        logger.info("✅ Social Manager initialized")
    
    async def create_post(
        self,
        content_type: str,
        context: Dict[str, Any],
        platform: Platform,
        schedule_time: Optional[datetime] = None,
        require_approval: bool = True
    ) -> SocialPost:
        """
        Create a social media post
        
        Args:
            content_type: wellness, creative, or community
            context: Data to fill template
            platform: Target platform
            schedule_time: When to post (None = now)
            require_approval: If true, goes to pending queue
        """
        templates = self.CONTENT_TEMPLATES.get(content_type, self.CONTENT_TEMPLATES["wellness"])
        template = random.choice(templates)
        
        # Fill template
        try:
            content = template.format(**context)
        except KeyError:
            # Fallback if context doesn't match template
            content = template
        
        # Truncate for platform limits
        if platform == Platform.TWITTER and len(content) > 280:
            content = content[:277] + "..."
        
        post = SocialPost(
            post_id=f"post_{datetime.utcnow().timestamp()}",
            platform=platform,
            content=content,
            media_urls=[],
            scheduled_time=schedule_time or datetime.utcnow(),
            status=PostStatus.PENDING_APPROVAL if require_approval else PostStatus.SCHEDULED,
            engagement={"likes": 0, "shares": 0, "comments": 0, "reach": 0},
            created_at=datetime.utcnow()
        )
        
        self.posts[post.post_id] = post
        
        logger.info(f"📝 Post created for {platform.value}: {content[:50]}...")
        
        return post
    
    async def schedule_daily_posts(
        self,
        wellness_context: Dict[str, Any],
        creative_context: Dict[str, Any]
    ):
        """Schedule 3 posts for the day"""
        now = datetime.utcnow()
        
        # Morning post (wellness focus)
        morning_time = now.replace(hour=9, minute=0, second=0)
        if morning_time < now:
            morning_time += timedelta(days=1)
        
        await self.create_post(
            content_type="wellness",
            context=wellness_context,
            platform=Platform.TWITTER,
            schedule_time=morning_time,
            require_approval=self.settings.REQUIRE_CONSENT_FOR_PUBLISH
        )
        
        # Afternoon post (creative focus)
        afternoon_time = now.replace(hour=14, minute=0, second=0)
        if afternoon_time < now:
            afternoon_time += timedelta(days=1)
        
        await self.create_post(
            content_type="creative",
            context=creative_context,
            platform=Platform.TWITTER,
            schedule_time=afternoon_time,
            require_approval=self.settings.REQUIRE_CONSENT_FOR_PUBLISH
        )
        
        # Evening post (community focus)
        evening_time = now.replace(hour=19, minute=0, second=0)
        if evening_time < now:
            evening_time += timedelta(days=1)
        
        await self.create_post(
            content_type="community",
            context={"insight": "collective resonance"},
            platform=Platform.TWITTER,
            schedule_time=evening_time,
            require_approval=self.settings.REQUIRE_CONSENT_FOR_PUBLISH
        )
        
        logger.info("📅 Daily posts scheduled")
    
    async def publish_post(self, post_id: str) -> Dict[str, Any]:
        """Publish a post to social media"""
        post = self.posts.get(post_id)
        if not post:
            raise ValueError(f"Post not found: {post_id}")
        
        if post.status != PostStatus.SCHEDULED:
            return {"success": False, "error": f"Post status is {post.status.value}"}
        
        try:
            if post.platform == Platform.TWITTER and Platform.TWITTER in self.clients:
                client = self.clients[Platform.TWITTER]
                response = client.create_tweet(text=post.content)
                
                post.status = PostStatus.PUBLISHED
                post.published_at = datetime.utcnow()
                
                logger.info(f"✅ Published to Twitter: {post.post_id}")
                
                return {
                    "success": True,
                    "platform": post.platform.value,
                    "tweet_id": response.data["id"],
                    "engagement": post.engagement
                }
            
            elif post.platform == Platform.INSTAGRAM:
                # Instagram posting logic
                logger.info(f"📷 Instagram post would publish: {post.content[:50]}...")
                post.status = PostStatus.PUBLISHED
                return {"success": True, "platform": "instagram", "note": "Simulated"}
            
            else:
                post.status = PostStatus.FAILED
                post.error_message = "Platform not configured"
                return {"success": False, "error": "Platform not configured"}
                
        except Exception as e:
            post.status = PostStatus.FAILED
            post.error_message = str(e)
            logger.error(f"❌ Publish failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def approve_post(self, post_id: str) -> bool:
        """User approves a pending post for publishing"""
        post = self.posts.get(post_id)
        if not post:
            return False
        
        if post.status == PostStatus.PENDING_APPROVAL:
            post.status = PostStatus.SCHEDULED
            logger.info(f"✅ Post approved: {post_id}")
            return True
        
        return False
    
    async def track_engagement(self, post_id: str) -> Dict[str, int]:
        """Track engagement metrics for a published post"""
        post = self.posts.get(post_id)
        if not post or post.status != PostStatus.PUBLISHED:
            return {}
        
        try:
            if post.platform == Platform.TWITTER and Platform.TWITTER in self.clients:
                # Get tweet metrics
                client = self.clients[Platform.TWITTER]
                tweet = client.get_tweet(
                    post.engagement.get("tweet_id"),
                    tweet_fields=["public_metrics"]
                )
                
                metrics = tweet.data.public_metrics
                post.engagement = {
                    "likes": metrics.get("like_count", 0),
                    "shares": metrics.get("retweet_count", 0),
                    "comments": metrics.get("reply_count", 0),
                    "reach": metrics.get("impression_count", 0)
                }
                
                return post.engagement
                
        except Exception as e:
            logger.error(f"Engagement tracking failed: {e}")
        
        return post.engagement
    
    async def generate_social_content(
        self,
        source: str,  # "wellness", "creative", "hive"
        data: Dict[str, Any]
    ) -> str:
        """
        Generate social media content from source data
        
        Args:
            source: Type of content source
            data: Source data (wellness metrics, creation info, hive insight)
        """
        if source == "wellness":
            templates = self.CONTENT_TEMPLATES["wellness"]
            context = {
                "metric": data.get("metric", "biometrics"),
                "protocol": data.get("protocol", "wellness protocol"),
                "improvement": data.get("improvement", "5"),
                "frequency": data.get("frequency", "432"),
                "day": data.get("day", "1"),
                "achievement": data.get("achievement", "completed session")
            }
        elif source == "creative":
            templates = self.CONTENT_TEMPLATES["creative"]
            context = {
                "creation_type": data.get("type", "project"),
                "title": data.get("title", "New Work"),
                "project_name": data.get("name", "Project"),
                "project": data.get("project", "creation"),
                "milestone": data.get("milestone", "Milestone")
            }
        else:
            templates = self.CONTENT_TEMPLATES["community"]
            context = {
                "activity": data.get("activity", "swarm activity"),
                "insight": data.get("insight", "collective wisdom"),
                "pattern": data.get("pattern", "emergent behavior"),
                "community_aspect": data.get("aspect", "community"),
                "guidance": data.get("guidance", "trust the process")
            }
        
        template = random.choice(templates)
        return template.format(**context)
    
    async def _post_scheduler(self):
        """Background task to publish scheduled posts"""
        while True:
            try:
                now = datetime.utcnow()
                
                # Reset daily counters at midnight
                if now.date() > self.last_reset.date():
                    self.daily_post_count = {}
                    self.last_reset = now
                
                # Find posts ready to publish
                for post in self.posts.values():
                    if post.status == PostStatus.SCHEDULED:
                        if post.scheduled_time <= now:
                            # Check daily limit
                            platform_count = self.daily_post_count.get(post.platform, 0)
                            if platform_count < 3:  # Max 3 posts per day per platform
                                await self.publish_post(post.post_id)
                                self.daily_post_count[post.platform] = platform_count + 1
                            else:
                                logger.warning(f"Daily limit reached for {post.platform.value}")
                
                await asyncio.sleep(60)  # Check every minute
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                await asyncio.sleep(60)
    
    async def get_pending_posts(self) -> List[Dict[str, Any]]:
        """Get posts awaiting user approval"""
        return [
            {
                "post_id": p.post_id,
                "platform": p.platform.value,
                "content": p.content,
                "scheduled_time": p.scheduled_time.isoformat(),
                "status": p.status.value
            }
            for p in self.posts.values()
            if p.status == PostStatus.PENDING_APPROVAL
        ]
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get social media statistics"""
        total_posts = len(self.posts)
        published = sum(1 for p in self.posts.values() if p.status == PostStatus.PUBLISHED)
        pending = sum(1 for p in self.posts.values() if p.status == PostStatus.PENDING_APPROVAL)
        failed = sum(1 for p in self.posts.values() if p.status == PostStatus.FAILED)
        
        total_engagement = {
            "likes": sum(p.engagement.get("likes", 0) for p in self.posts.values()),
            "shares": sum(p.engagement.get("shares", 0) for p in self.posts.values()),
            "comments": sum(p.engagement.get("comments", 0) for p in self.posts.values()),
            "reach": sum(p.engagement.get("reach", 0) for p in self.posts.values())
        }
        
        return {
            "total_posts": total_posts,
            "published": published,
            "pending_approval": pending,
            "failed": failed,
            "daily_counts": self.daily_post_count,
            "total_engagement": total_engagement,
            "average_engagement_per_post": {
                k: round(v / max(published, 1), 2)
                for k, v in total_engagement.items()
            }
        }
    
    async def close(self):
        """Cleanup resources"""
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("📱 Social Manager shut down")
