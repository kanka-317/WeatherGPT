import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../models/chat_message.dart';

class ChatBubbleWidget extends StatefulWidget {
  final ChatMessageModel message;
  final VoidCallback? onSpeak;

  const ChatBubbleWidget({
    super.key,
    required this.message,
    this.onSpeak,
  });

  @override
  State<ChatBubbleWidget> createState() => _ChatBubbleWidgetState();
}

class _ChatBubbleWidgetState extends State<ChatBubbleWidget> {
  bool _showExplainability = false;

  @override
  Widget build(BuildContext context) {
    final isUser = widget.message.role == 'user';

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Column(
        crossAxisAlignment: isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
        children: [
          // Bubble Body
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.82,
            ),
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: isUser
                  ? const Color(0xFF0284C7) // Sky blue for user
                  : AppColors.surfaceCard, // Deep surface card for assistant
              borderRadius: BorderRadius.only(
                topLeft: const Radius.circular(18),
                topRight: const Radius.circular(18),
                bottomLeft: Radius.circular(isUser ? 18 : 4),
                bottomRight: Radius.circular(isUser ? 4 : 18),
              ),
              border: Border.all(
                color: isUser ? Colors.transparent : AppColors.surfaceBorder,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.2),
                  blurRadius: 8,
                  offset: const Offset(0, 3),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Role tag if assistant has specific persona
                if (!isUser && widget.message.userRole != null && widget.message.userRole != 'citizen') ...[
                  Container(
                    margin: const EdgeInsets.only(bottom: 6),
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.primaryCyan.withOpacity(0.15),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: AppColors.primaryCyan.withOpacity(0.3)),
                    ),
                    child: Text(
                      '${widget.message.userRole!.toUpperCase()} ADVISORY',
                      style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: AppColors.primaryCyan),
                    ),
                  ),
                ],

                // Message Text
                Text(
                  widget.message.content,
                  style: TextStyle(
                    fontSize: 14.5,
                    height: 1.4,
                    color: isUser ? Colors.white : AppColors.textPrimary,
                  ),
                ),

                const SizedBox(height: 6),

                // Bottom Meta Bar (Timestamp + Audio Button)
                Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      widget.message.formattedTime,
                      style: TextStyle(
                        fontSize: 10,
                        color: isUser ? Colors.white70 : AppColors.textMuted,
                      ),
                    ),
                    if (!isUser && widget.onSpeak != null) ...[
                      const SizedBox(width: 8),
                      InkWell(
                        onTap: widget.onSpeak,
                        child: const Padding(
                          padding: EdgeInsets.all(2),
                          child: Icon(Icons.volume_up_rounded, size: 16, color: AppColors.primaryCyan),
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ),
          ),

          // Explainability Panel ("Why this answer" accordion)
          if (!isUser && widget.message.explainabilitySummary != null) ...[
            const SizedBox(height: 4),
            Container(
              constraints: BoxConstraints(
                maxWidth: MediaQuery.of(context).size.width * 0.82,
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  InkWell(
                    onTap: () => setState(() => _showExplainability = !_showExplainability),
                    borderRadius: BorderRadius.circular(8),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 4),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            _showExplainability ? Icons.info : Icons.info_outline,
                            size: 14,
                            color: AppColors.primaryCyan,
                          ),
                          const SizedBox(width: 4),
                          const Text(
                            'Why this answer?',
                            style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: AppColors.primaryCyan,
                            ),
                          ),
                          Icon(
                            _showExplainability ? Icons.keyboard_arrow_up : Icons.keyboard_arrow_down,
                            size: 14,
                            color: AppColors.primaryCyan,
                          ),
                        ],
                      ),
                    ),
                  ),

                  if (_showExplainability) ...[
                    Container(
                      margin: const EdgeInsets.only(top: 4),
                      padding: const EdgeInsets.all(12),
                      decoration: BoxDecoration(
                        color: AppColors.surfaceElevated,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: AppColors.surfaceBorder),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.verified_user_rounded, size: 14, color: AppColors.accentEmerald),
                              const SizedBox(width: 6),
                              Text(
                                'Source: ${widget.message.dataSource ?? "OpenWeather & IMD"}',
                                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                              ),
                            ],
                          ),
                          const SizedBox(height: 4),
                          Text(
                            widget.message.explainabilitySummary!,
                            style: const TextStyle(fontSize: 11, color: AppColors.textSecondary, height: 1.3),
                          ),
                          if (widget.message.toolsCalled.isNotEmpty) ...[
                            const SizedBox(height: 6),
                            Wrap(
                              spacing: 4,
                              children: widget.message.toolsCalled.map((tool) {
                                return Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: AppColors.background,
                                    borderRadius: BorderRadius.circular(4),
                                    border: Border.all(color: AppColors.surfaceBorder),
                                  ),
                                  child: Text(
                                    'tool: $tool',
                                    style: const TextStyle(fontSize: 9, color: AppColors.textMuted, fontFamily: 'monospace'),
                                  ),
                                );
                              }).toList(),
                            ),
                          ],
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
