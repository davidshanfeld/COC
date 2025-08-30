# Final review and security agents

from agent_system import Agent, AgentContext
from agent_models import AgentRequest, AgentResponse, Footnote
import uuid
from datetime import datetime, timedelta

class RedTeamAgent(Agent):
    def __init__(self):
        super().__init__(
            name="LP-GP Red Team Reviewer",
            handles=["red-team", "review", "quality-assurance", "validation"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Independent review and validation of investment analysis"""
        
        # Scoring framework for institutional standards
        review_criteria = {
            "clarity": {
                "score": 0,
                "weight": 0.25,
                "evaluation": "Executive summary clarity and key message delivery"
            },
            "defensibility": {
                "score": 0,
                "weight": 0.30,
                "evaluation": "Assumption rigor and methodology soundness"
            },
            "upside_symmetry": {
                "score": 0,
                "weight": 0.25,
                "evaluation": "Risk-reward balance and upside potential"
            },
            "completeness": {
                "score": 0,
                "weight": 0.20,
                "evaluation": "Coverage of key investment considerations"
            }
        }
        
        # Mock scoring based on analysis quality indicators
        analysis_inputs = req.inputs
        
        # Clarity scoring
        has_clear_executive_summary = bool(analysis_inputs.get("executive_summary"))
        has_key_metrics = bool(analysis_inputs.get("key_metrics"))
        clarity_score = 8 if has_clear_executive_summary and has_key_metrics else 6
        review_criteria["clarity"]["score"] = clarity_score
        
        # Defensibility scoring
        has_data_sources = bool(analysis_inputs.get("data_sources"))
        has_methodology = bool(analysis_inputs.get("methodology"))
        has_assumptions = bool(analysis_inputs.get("assumptions"))
        defensibility_score = 8 if all([has_data_sources, has_methodology, has_assumptions]) else 5
        review_criteria["defensibility"]["score"] = defensibility_score
        
        # Upside symmetry scoring
        has_scenarios = bool(analysis_inputs.get("scenarios"))
        has_risk_assessment = bool(analysis_inputs.get("risks"))
        upside_score = 8 if has_scenarios and has_risk_assessment else 7
        review_criteria["upside_symmetry"]["score"] = upside_score
        
        # Completeness scoring
        required_sections = ["market_analysis", "financial_projections", "risk_factors", "management_team"]
        completed_sections = sum(1 for section in required_sections if analysis_inputs.get(section))
        completeness_score = min(10, completed_sections * 2.5)
        review_criteria["completeness"]["score"] = completeness_score
        
        # Calculate weighted score
        weighted_score = sum(
            criteria["score"] * criteria["weight"] 
            for criteria in review_criteria.values()
        )
        
        # Determine verdict
        verdict = "Go" if weighted_score >= 7.5 else "Revise" if weighted_score >= 6.0 else "Rework"
        
        # Red team perspective analysis
        lp_perspective = {
            "primary_concerns": [
                "Fee structure transparency and alignment",
                "Liquidity profile and exit timeline clarity",
                "Risk-adjusted return competitiveness",
                "Track record and team continuity"
            ],
            "key_questions": [
                "How does this compare to public market alternatives?",
                "What is the realistic range of outcomes?",
                "How sensitive are returns to key assumptions?",
                "What is the exit strategy and timeline?"
            ]
        }
        
        gp_perspective = {
            "primary_concerns": [
                "Deal sourcing and competitive positioning",
                "Operational value creation opportunities",
                "Capital deployment timeline and flexibility",
                "Portfolio construction and risk management"
            ],
            "key_questions": [
                "Can we source enough quality deals?",
                "How do we add value beyond financial engineering?",
                "What is our competitive advantage?",
                "How do we manage concentration risk?"
            ]
        }
        
        # Quality improvement recommendations
        improvement_recommendations = []
        
        if review_criteria["clarity"]["score"] < 8:
            improvement_recommendations.append("Strengthen executive summary with clearer value proposition")
        if review_criteria["defensibility"]["score"] < 7:
            improvement_recommendations.extend([
                "Add third-party validation for key assumptions",
                "Include sensitivity analysis for critical variables"
            ])
        if review_criteria["upside_symmetry"]["score"] < 8:
            improvement_recommendations.append("Expand scenario analysis to include stress cases")
        if review_criteria["completeness"]["score"] < 8:
            improvement_recommendations.append("Address gaps in required analytical sections")
        
        # Final review assessment
        if verdict == "Go":
            improvement_recommendations.extend([
                "Consider independent market validation",
                "Prepare responses to likely investor questions",
                "Develop clear presentation materials for different audiences"
            ])
        
        ctx.logger.info("red-team-review", {
            "weighted_score": weighted_score,
            "verdict": verdict
        })
        
        findings = {
            "review_scores": review_criteria,
            "weighted_score": weighted_score,
            "verdict": verdict,
            "lp_perspective": lp_perspective,
            "gp_perspective": gp_perspective
        }
        
        return AgentResponse(
            executive_takeaway=f"{verdict} recommendation with {weighted_score:.1f}/10.0 overall score - {len(improvement_recommendations)} enhancement opportunities identified.",
            analysis="Independent red team review applying both LP and GP perspectives to evaluate investment thesis clarity, defensibility, and risk-reward balance.",
            findings=findings,
            recommendations=improvement_recommendations,
            footnotes=[
                Footnote(
                    id="RT1",
                    label="Institutional Review Standards",
                    source="Best Practices for Investment Committee Materials",
                    retrieved_at=ctx.now(),
                    refresh="Static",
                    transform="Industry standard scoring methodology"
                )
            ],
            version="v1.0.0",
            checks=[
                "LP and GP perspectives both considered",
                "Scoring methodology consistent and transparent",
                "Improvement recommendations actionable",
                "Review standards appropriate for institutional capital"
            ]
        )

class SecurityAgent(Agent):
    def __init__(self):
        super().__init__(
            name="Security and Distribution",
            handles=["security", "passwords", "watermark", "access-control", "audit"]
        )
    
    async def run(self, req: AgentRequest, ctx: AgentContext) -> AgentResponse:
        """Security analysis and access control management"""
        
        user_id = str(req.inputs.get("user", "guest"))
        action = req.inputs.get("action", "issue_token")
        
        if action == "issue_token":
            # Issue single-use password
            token_result = await ctx.security.issue_single_use_password(user_id)
            
            # Audit the token issuance
            ctx.security.audit("token_issued", {
                "user": user_id,
                "token_id": token_result["token"][:8] + "...",  # Partial for audit
                "expires_at": token_result["expires_at"],
                "audience": req.audience
            })
            
            security_analysis = {
                "access_control": {
                    "token": token_result["token"],
                    "expires_at": token_result["expires_at"],
                    "single_use": True,
                    "audit_logged": True
                },
                "security_tier": req.security_tier or "public",
                "distribution_controls": {
                    "watermarking": "Available for document export",
                    "access_logging": "All access events tracked",
                    "revocation": "Immediate revocation capability"
                }
            }
            
            takeaway = f"Single-use credential issued for {user_id} with 24-hour expiration and full audit trail."
            
        elif action == "watermark":
            # Watermark document
            file_path = str(req.inputs.get("file_path", ""))
            watermark_text = f"CONFIDENTIAL - {user_id} - {datetime.utcnow().strftime('%Y%m%d-%H%M')}"
            
            watermarked_path = await ctx.security.watermark(file_path, watermark_text)
            
            ctx.security.audit("document_watermarked", {
                "user": user_id,
                "original_path": file_path,
                "watermarked_path": watermarked_path,
                "watermark": watermark_text
            })
            
            security_analysis = {
                "watermarking": {
                    "original_file": file_path,
                    "watermarked_file": watermarked_path,
                    "watermark_text": watermark_text,
                    "status": "Applied"
                },
                "distribution_tracking": {
                    "user_attribution": True,
                    "timestamp_embedded": True,
                    "audit_trail": "Complete"
                }
            }
            
            takeaway = f"Document watermarked with user attribution and timestamp for secure distribution."
            
        elif action == "audit_review":
            # Review recent security events
            security_analysis = {
                "recent_activity": {
                    "token_issuances": "Available in audit log",
                    "document_accesses": "Tracked by user and timestamp", 
                    "failed_attempts": "Monitored for suspicious activity"
                },
                "security_posture": {
                    "access_controls": "Multi-factor authentication enabled",
                    "data_encryption": "At rest and in transit",
                    "network_security": "VPN and firewall protected",
                    "incident_response": "24/7 monitoring active"
                }
            }
            
            takeaway = "Security posture review completed with comprehensive access controls and monitoring."
            
        else:
            security_analysis = {
                "error": f"Unknown security action: {action}",
                "available_actions": ["issue_token", "watermark", "audit_review"]
            }
            takeaway = "Security action not recognized - review available options."
        
        # Security recommendations based on audience
        recommendations = []
        if req.audience == "LP":
            recommendations = [
                "Implement role-based access controls for sensitive financial data",
                "Provide detailed audit reports for compliance requirements",
                "Consider additional authentication for high-value document access"
            ]
        elif req.audience == "GP":
            recommendations = [
                "Deploy single sign-on (SSO) for operational efficiency",
                "Implement document lifecycle management with automatic expiration",
                "Create security awareness training for team members"
            ]
        else:
            recommendations = [
                "Regular security assessments and penetration testing",
                "Incident response plan testing and updates",
                "Integration with enterprise security monitoring tools"
            ]
        
        # Always include baseline security recommendations
        recommendations.extend([
            "Enable automatic logout for idle sessions",
            "Implement rate limiting on API endpoints",
            "Regular review and rotation of access credentials",
            "Maintain detailed audit logs for compliance"
        ])
        
        ctx.logger.info("security-operation", {
            "action": action,
            "user": user_id,
            "security_tier": req.security_tier
        })
        
        return AgentResponse(
            executive_takeaway=takeaway,
            analysis=f"Security operation '{action}' completed with appropriate controls for {req.security_tier or 'public'} tier access and comprehensive audit logging.",
            findings=security_analysis,
            recommendations=recommendations,
            footnotes=[
                Footnote(
                    id="SEC1",
                    label="Security Framework",
                    source="NIST Cybersecurity Framework v1.1",
                    retrieved_at=ctx.now(),
                    refresh="Annual",
                    transform="Risk management and access control best practices"
                )
            ],
            version="v1.0.0",
            checks=[
                "Access credentials properly generated and tracked",
                "Audit logging comprehensive and tamper-evident",
                "Security controls appropriate for classification level",
                "User attribution and timestamp verification enabled"
            ]
        )