"""
Document Routes
Document generation and management routes

© 2025-2030 Ashutosh Sinha, ajsinha@gmail.com, https://www.github.com/ajsinha/abhikarta
"""

import os
import re
from flask import session, render_template, request, jsonify
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'md', 'csv', 'json'}
MAX_FILES = 10


class DocumentRoutes:
    """Document generation routes handler"""

    def __init__(self, app, user_registry, login_required):
        """
        Initialize document routes

        Args:
            app: Flask application instance
            user_registry: User registry instance
            login_required: Login required decorator
        """
        self.app = app
        self.user_registry = user_registry
        self.login_required = login_required
        self.register_routes()

    def register_routes(self):
        """Register all document routes"""

        @self.app.route('/document-generation')
        @self.login_required
        def document_generation():
            """Document generation page"""
            user = self.user_registry.get_user(session['user_id'])
            return render_template('document_generate.html', user=user)

        @self.app.route('/api/document/create-session', methods=['POST'])
        @self.login_required
        def create_document_session():
            """Create a new document generation session"""
            user = self.user_registry.get_user(session['user_id'])
            data = request.get_json()
            session_name = data.get('session_name', '').strip()

            # Validate session name
            if not session_name:
                return jsonify({'success': False, 'error': 'Session name is required'}), 400

            # Check if session name contains at least one alphabetic character
            if not re.search(r'[a-zA-Z]', session_name):
                return jsonify({'success': False, 'error': 'Session name must contain at least one alphabetic character'}), 400

            # Check if session name contains only alphanumerics and underscores
            if not re.match(r'^[a-zA-Z0-9_]+$', session_name):
                return jsonify({'success': False, 'error': 'Session name can only contain alphanumerics and underscores'}), 400

            # Create session folder structure
            base_path = os.path.join('data', 'uploads', str(user.user_id), 'docgen', session_name)
            inbox_path = os.path.join(base_path, 'inbox')
            outbox_path = os.path.join(base_path, 'outbox')
            servermessages_path = os.path.join(base_path, 'servermessages')

            try:
                # Create all three folders
                os.makedirs(inbox_path, exist_ok=True)
                os.makedirs(outbox_path, exist_ok=True)
                os.makedirs(servermessages_path, exist_ok=True)

                return jsonify({
                    'success': True,
                    'message': f'Session "{session_name}" created successfully',
                    'session_path': base_path,
                    'inbox_path': inbox_path,
                    'outbox_path': outbox_path,
                    'servermessages_path': servermessages_path
                })
            except Exception as e:
                return jsonify({'success': False, 'error': f'Failed to create session: {str(e)}'}), 500

        @self.app.route('/api/document/upload', methods=['POST'])
        @self.login_required
        def upload_documents():
            """Upload documents to session inbox folder"""
            user = self.user_registry.get_user(session['user_id'])
            session_name = request.form.get('session_name')

            if not session_name:
                return jsonify({'success': False, 'error': 'Session name is required'}), 400

            # Check if files were uploaded
            if 'files' not in request.files:
                return jsonify({'success': False, 'error': 'No files uploaded'}), 400

            files = request.files.getlist('files')

            # Check file count
            if len(files) > MAX_FILES:
                return jsonify({'success': False, 'error': f'Maximum {MAX_FILES} files allowed'}), 400

            # Path to inbox folder
            inbox_path = os.path.join('data', 'uploads', str(user.user_id), 'docgen', session_name, 'inbox')

            if not os.path.exists(inbox_path):
                return jsonify({'success': False, 'error': 'Session folder does not exist. Please create a session first.'}), 400

            uploaded_files = []

            try:
                for file in files:
                    if file.filename == '':
                        continue

                    if file and self._allowed_file(file.filename):
                        filename = secure_filename(file.filename)
                        file_path = os.path.join(inbox_path, filename)
                        file.save(file_path)
                        uploaded_files.append(filename)
                    else:
                        return jsonify({'success': False, 'error': f'File type not allowed: {file.filename}'}), 400

                return jsonify({
                    'success': True,
                    'message': f'{len(uploaded_files)} file(s) uploaded successfully',
                    'files': uploaded_files
                })
            except Exception as e:
                return jsonify({'success': False, 'error': f'Upload failed: {str(e)}'}), 500

        @self.app.route('/api/document/generate', methods=['POST'])
        @self.login_required
        def generate_document():
            """Generate document based on uploaded files and instructions"""
            user = self.user_registry.get_user(session['user_id'])
            data = request.get_json()

            session_name = data.get('session_name', '').strip()
            template = data.get('template', 'Default')
            instructions = data.get('instructions', '').strip()

            if not session_name:
                return jsonify({'success': False, 'error': 'Session name is required'}), 400

            # Get uploaded files from inbox
            inbox_path = os.path.join('data', 'uploads', str(user.user_id), 'docgen', session_name, 'inbox')
            outbox_path = os.path.join('data', 'uploads', str(user.user_id), 'docgen', session_name, 'outbox')

            if not os.path.exists(inbox_path):
                return jsonify({'success': False, 'error': 'Session not found'}), 404

            # Create "started" status file in outbox
            try:
                # Remove any existing status files first
                for status_file in ['started', 'success', 'error']:
                    status_path = os.path.join(outbox_path, status_file)
                    if os.path.exists(status_path):
                        os.remove(status_path)

                # Create "started" file
                with open(os.path.join(outbox_path, 'started'), 'w') as f:
                    f.write('Document generation started')
            except Exception as e:
                pass  # Continue even if status file creation fails

            uploaded_files = [f for f in os.listdir(inbox_path) if os.path.isfile(os.path.join(inbox_path, f))]

            # Generate document content (hardcoded for now)
            generated_content = self._generate_document_content(session_name, template, instructions, uploaded_files)

            return jsonify({
                'success': True,
                'content': generated_content,
                'session_name': session_name,
                'template': template,
                'files_processed': len(uploaded_files)
            })

        @self.app.route('/api/document/status', methods=['POST'])
        @self.login_required
        def check_document_status():
            """Check document generation status by looking for status files in outbox"""
            user = self.user_registry.get_user(session['user_id'])
            data = request.get_json()

            session_name = data.get('session_name', '').strip()

            if not session_name:
                return jsonify({'success': False, 'error': 'Session name is required'}), 400

            # Get outbox path
            outbox_path = os.path.join('data', 'uploads', str(user.user_id), 'docgen', session_name, 'outbox')

            if not os.path.exists(outbox_path):
                return jsonify({'success': True, 'status': 'preparation'}), 200

            # Check for status files in priority order
            if os.path.exists(os.path.join(outbox_path, 'error')):
                return jsonify({'success': True, 'status': 'error'})
            elif os.path.exists(os.path.join(outbox_path, 'success')):
                return jsonify({'success': True, 'status': 'complete'})
            elif os.path.exists(os.path.join(outbox_path, 'started')):
                return jsonify({'success': True, 'status': 'waiting'})
            else:
                return jsonify({'success': True, 'status': 'preparation'})

        @self.app.route('/api/document/delete-file', methods=['POST'])
        @self.login_required
        def delete_file():
            """Delete a file from the session inbox"""
            user = self.user_registry.get_user(session['user_id'])
            data = request.get_json()

            session_name = data.get('session_name', '').strip()
            filename = data.get('filename', '').strip()

            if not session_name:
                return jsonify({'success': False, 'error': 'Session name is required'}), 400

            if not filename:
                return jsonify({'success': False, 'error': 'Filename is required'}), 400

            # Path to the file in inbox
            inbox_path = os.path.join('data', 'uploads', str(user.user_id), 'docgen', session_name, 'inbox')
            file_path = os.path.join(inbox_path, secure_filename(filename))

            if not os.path.exists(inbox_path):
                return jsonify({'success': False, 'error': 'Session not found'}), 404

            if not os.path.exists(file_path):
                return jsonify({'success': False, 'error': 'File not found'}), 404

            try:
                # Delete the file
                os.remove(file_path)
                return jsonify({
                    'success': True,
                    'message': f'File "{filename}" deleted successfully'
                })
            except Exception as e:
                return jsonify({'success': False, 'error': f'Failed to delete file: {str(e)}'}), 500

        @self.app.route('/api/document/rerun', methods=['POST'])
        @self.login_required
        def rerun_generation():
            """Rerun document generation with current editor content"""
            user = self.user_registry.get_user(session['user_id'])
            data = request.get_json()

            session_name = data.get('session_name', '').strip()
            template = data.get('template', 'Default')
            instructions = data.get('instructions', '').strip()
            current_content = data.get('current_content', '').strip()

            if not session_name:
                return jsonify({'success': False, 'error': 'Session name is required'}), 400

            # Get uploaded files from inbox (for context)
            inbox_path = os.path.join('data', 'uploads', str(user.user_id), 'docgen', session_name, 'inbox')

            if not os.path.exists(inbox_path):
                return jsonify({'success': False, 'error': 'Session not found'}), 404

            uploaded_files = [f for f in os.listdir(inbox_path) if os.path.isfile(os.path.join(inbox_path, f))]

            # For now, return the same hardcoded content (can be enhanced later to process current_content)
            # In a real implementation, you might:
            # - Parse current_content and enhance it
            # - Use LLM to regenerate based on current_content
            # - Apply additional processing

            generated_content = self._generate_document_content(session_name, template, instructions, uploaded_files)

            return jsonify({
                'success': True,
                'content': generated_content,
                'session_name': session_name,
                'template': template,
                'message': 'Document regenerated (current implementation uses same template)'
            })

    def _allowed_file(self, filename):
        """Check if file extension is allowed"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    def _generate_document_content(self, session_name, template, instructions, files):
        """Generate hardcoded document content"""

        if template == "CCR PFE":
            content = f"""# Customer Change Request - Pre-Flight Evaluation

## Session Information
**Session Name:** {session_name}  
**Template:** {template}  
**Date Generated:** {{ Current Date }}

## Executive Summary

This document presents a comprehensive pre-flight evaluation for the customer change request submitted in session **{session_name}**. The evaluation covers technical feasibility, resource requirements, risk assessment, and implementation recommendations.

## Files Analyzed

The following documents were processed as part of this evaluation:

"""
            for idx, file in enumerate(files, 1):
                content += f"{idx}. {file}\n"

            content += f"""

## User Instructions

{instructions if instructions else "*No specific instructions provided.*"}

## Technical Analysis

### 1. Feasibility Assessment

The proposed changes have been analyzed for technical feasibility across multiple dimensions:

- **Architecture Impact:** The changes align with current system architecture patterns and do not require significant refactoring.
- **Scalability Considerations:** The implementation can scale horizontally to meet projected load increases of up to 300%.
- **Integration Points:** All identified integration points are compatible with existing API contracts.

### 2. Resource Requirements

| Resource Type | Estimated Allocation | Notes |
|--------------|---------------------|-------|
| Development | 120 hours | Including unit testing |
| QA/Testing | 40 hours | Full regression suite |
| DevOps | 16 hours | CI/CD pipeline updates |
| Documentation | 24 hours | Technical and user docs |

### 3. Risk Assessment

**High Priority Risks:**

1. **Database Migration Complexity** - Medium Risk
   - Mitigation: Implement blue-green deployment strategy
   - Rollback plan: Automated snapshot restoration

2. **Third-Party API Dependencies** - Low Risk
   - Mitigation: Implement circuit breakers and fallback mechanisms
   - Monitoring: Real-time health checks every 30 seconds

**Medium Priority Risks:**

- Performance regression in legacy modules
- Compatibility issues with older client versions

## Implementation Recommendations

### Phase 1: Preparation (Week 1-2)
- Environment setup and configuration
- Database schema updates in staging
- Integration testing framework preparation

### Phase 2: Core Development (Week 3-5)
- Feature implementation
- Unit test coverage (target: 90%+)
- Code review and security audit

### Phase 3: Testing & Validation (Week 6-7)
- QA testing in staging environment
- Performance benchmarking
- User acceptance testing (UAT)

### Phase 4: Deployment (Week 8)
- Production deployment with monitoring
- Post-deployment validation
- Documentation handoff

## Cost-Benefit Analysis

**Estimated Costs:**
- Development: $24,000
- Infrastructure: $3,500
- Support & Maintenance (Year 1): $8,000

**Projected Benefits:**
- Operational efficiency gain: 25%
- User satisfaction improvement: 15-20%
- Annual cost savings: $45,000

**ROI Timeline:** 8-10 months

## Compliance & Security

All proposed changes comply with:
- SOC 2 Type II requirements
- GDPR data protection standards
- Industry-specific regulations (ISO 27001)

Security measures include:
- End-to-end encryption for sensitive data
- Role-based access control (RBAC)
- Comprehensive audit logging

## Conclusion

The proposed change request is **APPROVED** for implementation with the recommendations outlined above. The project demonstrates strong technical feasibility, acceptable risk levels, and clear business value.

**Next Steps:**
1. Schedule kick-off meeting with stakeholders
2. Finalize resource allocation
3. Begin Phase 1 activities within 2 weeks

---

*This document was generated by the Abhikarta Document Generation System*
"""
        else:  # Default template
            content = f"""# Document Generation Report

## Session Details

**Session Name:** {session_name}  
**Template Used:** {template}  
**Generation Date:** {{ Current Date }}

## Overview

This document has been generated based on the uploaded files and provided instructions for session **{session_name}**.

## Uploaded Files

The following files were processed:

"""
            for idx, file in enumerate(files, 1):
                content += f"{idx}. **{file}**\n"

            content += f"""

## User Instructions

{instructions if instructions else "*No specific instructions were provided for this session.*"}

## Document Summary

This section provides a comprehensive summary of the analyzed documents and their key findings.

### Key Highlights

- **Total Files Processed:** {len(files)}
- **Template Applied:** {template}
- **Processing Status:** Completed Successfully

### Analysis Results

The system has successfully processed all uploaded documents and applied the selected template to generate this comprehensive report. Below are the key insights derived from the analysis:

1. **Content Structure**
   - All documents were parsed and analyzed for structure and content
   - Key sections and metadata were extracted successfully
   - Cross-references between documents were identified

2. **Data Quality Assessment**
   - Format consistency: High
   - Completeness: 95%
   - Accuracy: Verified against standard templates

3. **Recommendations**
   - Consider consolidating similar content across documents
   - Standardize naming conventions for better organization
   - Implement version control for document tracking

## Detailed Findings

### Section 1: Content Analysis

The uploaded documents demonstrate a high level of organization and clarity. The content structure follows industry best practices and maintains consistency throughout.

**Strengths:**
- Clear hierarchical organization
- Comprehensive coverage of topics
- Well-documented references

**Areas for Improvement:**
- Enhanced visual elements could improve readability
- Additional cross-referencing between sections
- Expanded glossary of technical terms

### Section 2: Technical Review

Technical accuracy and completeness have been verified across all submitted documents.

**Validation Results:**
- Syntax: ✓ Passed
- Semantic consistency: ✓ Passed
- Reference integrity: ✓ Passed
- Format compliance: ✓ Passed

### Section 3: Recommendations

Based on the comprehensive analysis, the following recommendations are proposed:

1. **Immediate Actions**
   - Review and update outdated sections
   - Standardize formatting across all documents
   - Add version numbers and change logs

2. **Short-term Improvements** (1-3 months)
   - Implement automated validation checks
   - Create supplementary documentation
   - Establish review cycles

3. **Long-term Strategy** (3-6 months)
   - Develop comprehensive documentation framework
   - Integrate with knowledge management systems
   - Establish governance policies

## Conclusion

The document generation process has been completed successfully. All uploaded files have been processed according to the specifications, and this report provides a comprehensive overview of the findings and recommendations.

For questions or further assistance, please contact the system administrator or refer to the user documentation.

---

*Generated by Abhikarta Multi-Agent Orchestration System*  
*© 2025-2030 Ashutosh Sinha*
"""

        return content